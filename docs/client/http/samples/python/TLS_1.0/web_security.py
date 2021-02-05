#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Tintri, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import sys
import time
import getpass
import argparse
import tintri_1_1 as tintri

"""
 This script gets and sets the security protocols for the web server.

 Command usage: web_security --help

"""

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False
APPLIANCE_URL = "/v310/appliance/default"


def print_with_prefix(prefix, out):
    print(prefix + out)
    return


def print_debug(out):
    if debug_mode:
        print_with_prefix("[DEBUG] : ", out)
    return


def print_info(out):
    print_with_prefix("[INFO] : ", out)
    return


def print_error(out):
    print_with_prefix("[ERROR] : ", out)
    return


def pretty_json(json_input):
    return json.dumps(json_input, sort_keys=True, separators=(',',':'))


# Print TLS info.
def print_tls_protocols(tls_info, description):
    print(description + "protocols: " + ", ".join(tls_info))


# Return TLS protocols.
def get_tls_protocols(server_name, session_id):
    url = APPLIANCE_URL
    
    # Make the get invoke
    r = tintri.api_get(server_name, url, session_id)
    print_debug("The JSON response of the get appliance invoke to the server " +
                server_name + " is: " + r.text)
    
    appliance_resp = r.json()
    appliance_info = appliance_resp[0]
    if not 'httpsProtocols' in appliance_info:
        raise tintri.TintriRequestsException("No httpsProtocols:\n" + json.dumps(appliance_info, sort_keys=True, indent=4, separators=(',',':')))
        
    return appliance_info['httpsProtocols']




# Restarts the web server and waits for it to come back up.
def restart_web_server(server_name, session_id):
    print("Restarting web server")

    try:
        url = APPLIANCE_URL + "/restartWebServer"
    
        r = tintri.api_post(server_name, url, None, session_id)
        if (r.status_code != 204):
            msg = "The HTTP response for the post invoke to the server is " + \
                  server_name + " not 204, but is: " + str(r.status_code) + "."
            raise tintri.TintriApiException(msg, r.status_code, url, None, r.text)
    
        print_debug("The JSON response of the post invoke to the server " +
                    server_name + " is: " + r.text)

    # These exceptions don't do anything because we assume the
    # web server restart occured and killed the connection before
    # the response is returned.  This is a multi-thread issue in
    # the web servers.
    except tintri.TintriRequestsException as tre:
        pass
    except tintri.TintriApiException as tae:
        pass

    # Set up some variables
    sec_incr = 10
    max_seconds = 120
    sec_cntr = sec_incr
    restarted = False

    # Wait in 10 second intervals
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(sec_incr)

    while (sec_cntr < max_seconds):
        sys.stdout.write(".")
        sys.stdout.flush()

        try:
            # Get the version to check in the web server is back-up
            r = tintri.api_version(server_name)
            json_info = r.json()
            if (json_info):
                restarted = True
                break
    
        # These exceptions pass, because we expect failure until
        # the API works.
        except tintri.TintriRequestsException as tre:
            pass
        except tintri.TintriApiException as tae:
            pass

        sec_cntr += sec_incr
        time.sleep(sec_incr)

    if not restarted:
        print_error("Web server not restarted after " + str(max_seconds) + " seconds.")
        sys.exit(10)

    print("Web server restarted")


# Logins in after restarting server
def login_after_restart(server_name, user_name, password):
    session_id = ""

    # Set up some variables
    sec_incr = 10
    max_seconds = 60
    sec_cntr = sec_incr
    logged_in = False

    # Wait in 10 second intervals
    sys.stdout.write("Logging in .")
    sys.stdout.flush()
    time.sleep(sec_incr)

    while (sec_cntr < max_seconds):
        try:
            # Get the version to check in the web server is back-up
            session_id = tintri.api_login(server_name, user_name, password)
            logged_in = True
            break
    
        # These exceptions pass, because the server is not ready
        except tintri.TintriRequestsException as tre:
            pass
        except tintri.TintriApiException as tae:
            pass

        sec_cntr += sec_incr
        time.sleep(sec_incr)

        sys.stdout.write(".")
        sys.stdout.flush()

    if not logged_in:
        print_error("Couldn't log into " + server_name + " after " + str(max_seconds) + " seconds.")
        sys.exit(10)

    print("")
    return session_id


def show_examples():
    print ""
    print "Examples;"
    print "web_security.py -s <server>                   -- Retrieves the current web security protocol values"
    print "web_security.py --default -s <server>         -- Sets the default web security protocol values"
    print "web_security.py --protocols TLSv1 -s <server> -- Sets TLSv1 web security protocol value"
    print "web_security.py -p TLSv1 -s <server>          -- Sets TLSv1 web security protocol value"
    print "web_security.py -p TLSv1 TLSv1.1 -s <server>  -- Sets TLSv1 and TLSv1.1 web security protocol values"
    print ""


# main
set_default = False
set_protocols = False
server_set = False

protocols = []

# Get the command arguments.
parser = argparse.ArgumentParser(description="Gets and optionally sets web security protocols.")

parser.add_argument("--default",
                    action="store_true",
                    help="Sets the default security protocols.")
parser.add_argument("--examples",
                    action="store_true",
                    help="Lists usage examples")
parser.add_argument("--protocols", "-p",
                    nargs='+',
                    help="One or more security protocols.  " + \
                         "Valid protocols are:  'TLSv1', 'TLSv1.1', 'TLSv1.2', and 'SSLv2Hello'.")
parser.add_argument("--server", "-s",
                    nargs=1,
                    help="Tintri server name.  (Required except for --examples)")

args = parser.parse_args()
server_name = args.server

if args.examples:
    show_examples()
    sys.exit(0)

if args.server:
    server_name = args.server[0]
    server_set = True

if args.default:
    set_default = True

if args.protocols != None:
    if set_default:
        print_info("Ignoring default options")
        set_default = False

    set_protocols = True
    if ',' in args.protocols:
        protocols = args.protocols.split(",")
    else:
        protocols = args.protocols

    if (len(protocols) == 1 and protocols[0] == "SSLv2Hello"):
        print_error("Need at least one TLS protocol specified with 'SSLv2Hello'")
        sys.exit(1)

    if debug_mode:
        print("protocols: ")
        count = 1
        for protocol in protocols:
            print("  " + str(count) + ": " + protocol)
            count += 1

if (not server_set):
    print("--server|-s is required for --default and --protocols|-p")
    sys.exit(1)

# Credentials Gathering - support Python 2.X and 3.X
try: 
	user_name = raw_input("Enter user name: ")
except NameError:
	user_name = input("Enter user name: ")
password = getpass.getpass("Enter password: ")
print("")

try:
    # Get the preferred version
    r = tintri.api_version(server_name)
    json_info = r.json()
    preferred_version = json_info['preferredVersion']
    product_name = json_info['productName']
    print_info(product_name + " running " + "API version " + preferred_version)

    session_id = tintri.api_login(server_name, user_name, password)

except tintri.TintriRequestsException as tre:
    print_error(tre.__str__())
    sys.exit(-2)
except tintri.TintriApiException as tae:
    print_error(tae.__str__())
    sys.exit(-3)

try:
    tls_info = get_tls_protocols(server_name, session_id)
    print_tls_protocols(tls_info, "Current ")
    print ""
    
    new_tls_info = []

    if (set_default or set_protocols):

        if set_default:
            protocols = ['TINTRI_DEFAULT']

        new_tls_info = protocols

        # Create the Appliance object with the new ApplianceDns DTO.
        new_appliance = \
            {'typeId': 'com.tintri.api.rest.v310.dto.domain.Appliance',
             'httpsProtocols': new_tls_info
            }
                     
        # Create the Request object with the Appliance DTO.
        Request = \
            {'typeId': 'com.tintri.api.rest.v310.dto.Request',
             'objectsWithNewValues': new_appliance,
             'propertiesToBeUpdated': ['httpsProtocols']
            }
            
        print_debug("Request:\n    " + pretty_json(Request))

        url = APPLIANCE_URL
        r = tintri.api_put(server_name, url, Request, session_id)
        print_debug("The JSON response of the get invoke to the server " +
                    server_name + " is: " + r.text)
            
        # if HTTP Response is not 204 then raise exception
        if r.status_code != 204:
            tintri.api_logout(server_name, session_id)
            message = "The HTTP response for put invoke to the server is not 204."
            raise tintri.TintriApiException(message, r.status_code, url, str(Request), r.text)
        
        # Wait a litle for settings to propagate.
        time.sleep(2)

        restart_web_server(server_name, session_id)

    
        # Need to re-login after web server restart
        session_id = login_after_restart(server_name, user_name, password)

        tls_info = get_tls_protocols(server_name, session_id)
        print_tls_protocols(tls_info, "Now ")
        print ""
    
except tintri.TintriRequestsException as tre:
    print_error(tre.__str__())
    sys.exit(-4)
except tintri.TintriApiException as tae:
    print_error(tae.__str__())
    sys.exit(-5)
    
# All pau, log out
tintri.api_logout(server_name, session_id)
