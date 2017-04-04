#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Tintri, Inc.
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

import sys
import json
import time
import tintri_1_1 as tintri
from types import *
import datetime


"""
 Collect VM historic stats

"""

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False


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


def my_timezone():
    tz_hours = time.timezone / -3600
    tz_minutes = time.timezone % 3600
    return "{0:0=+3d}:{1:0=2d}".format(tz_hours, tz_minutes)


def print_stats(paged_result, count):
    page = paged_result["page"]
    page_total = paged_result["pageTotal"]
    print_info("Page " + str(page) + " of " + str(page_total))

    items = paged_result["items"]
    #print_info("items: " + str(items))
    for stat in items:
        num_slices = stat["numberOfSlices"]
        start_time = stat["startTime"]
        print("   " + start_time + " with " + str(num_slices) + " slices")

        historic_stats = stat["sortedStats"]
        for historic_stat in historic_stats:
            start_time = historic_stat["timeStart"]
            space_used = historic_stat["spaceUsedGiB"]
            print(str(count) + ": " + start_time + ": " + str(space_used))
            count += 1

    return count
    

# main
if len(sys.argv) < 4:
    print("\nCollect VM historic stats")
    print("Usage: " + sys.argv[0] + " server_name user_name password <page_size>\n")
    sys.exit(-1)

server_name = sys.argv[1]
user_name = sys.argv[2]
password = sys.argv[3]
page_size = 25  # init default
if len(sys.argv) == 5:
    page_size = sys.argv[4]

try:
    # Get the preferred version
    r = tintri.api_version(server_name)
    json_info = r.json()

    print_info("API Version: " + json_info['preferredVersion'])

    # Login to VMstore
    session_id = tintri.api_login(server_name, user_name, password)

except tintri.TintriRequestsException as tre:
    print_error(tre.__str__())
    sys.exit(-10)
except tintri.TintriApiException as tae:
    print_error(tae.__str__())
    sys.exit(-11)
    
try:
    # Get a VM to work with
    vm_filter = {'limit'  : 1,
                 'sortedBy' : 'LATENCY',
                 'sortOrder' : 'DESC',
                 'live'   : "TRUE"}
    url = "/v310/vm"
    r = tintri.api_get_query(server_name, url, vm_filter, session_id)
    print_debug("The JSON response of the get invoke to the server " +
                server_name + " is: " + r.text)
        
    if (r.status_code != 200):
        msg = "The HTTP response for the get invoke to the server is " + \
              server_name + "not 200, but is: " + str(r.status_code) + "."
        raise tintri.TintriApiException(msg, r.status_code, url, str(vm_filter), r.text)
    
    vm_paginated_result = r.json()
    items = vm_paginated_result['items']
    vm = items[0]
    vm_uuid = vm['uuid']['uuid']
    vm_name = vm['vmware']['name']
    print_info("VM: " + vm_name + " : " + vm_uuid)
    
    # Get the time 30 minutes ago in UTC.
    now = datetime.datetime.utcnow()
    minus_30 = now - datetime.timedelta(minutes=30)

    # Add UTC time zone and print.
    now_str = now.isoformat() + "-00:00"
    minus_30_str = minus_30.isoformat() + "-00:00"
    print_info("                   Now: " + now_str)
    print_info("Collectiong stats from: " + minus_30_str)

    q_filter = {#'queryType': 'TOP_DOCS_BY_LATEST_TIME',
                'since'    : minus_30_str,
                'offset'   : 0,
                'limit'    : page_size }

    # Get historic stats
    historic_url = "/v310/vm/" + vm_uuid + "/statsHistoric"
    print_info("URL: " + historic_url + ", " + str(q_filter))
    r = tintri.api_get_query(server_name, historic_url, q_filter, session_id)
    print_debug("The JSON response of the get invoke to the server " +
                server_name + " is: " + r.text)
        
    if (r.status_code != 200):
        msg = "The HTTP response for the get invoke to the server is " + \
              server_name + "not 200, but is: " + str(r.status_code) + "."
        raise tintri.TintriApiException(msg, r.status_code, historic_url, str(q_filter), r.text)
    
    historic_paginated_result = r.json()
    print_info("Absolute Total: " + str(historic_paginated_result["absoluteTotal"]))
    
    count = 1
    print("   " + now.isoformat() + " is now")

    count = print_stats(historic_paginated_result, count)
    print_info("limit: " + str(historic_paginated_result['limit']))

    # While there are more Vms, go get them
    while 'next' in historic_paginated_result:
        url = historic_url + "?" + historic_paginated_result['next']
        print_info("Next GET URL: " + str(count) + ": " + url)
    
        r = tintri.api_get(server_name, url, session_id)
    
        historic_result = r.json()
        count = print_stats(historic_paginated_result, count)
    
except tintri.TintriRequestsException as tre:
    print_error(tre.__str__())
    tintri.api_logout(server_name, session_id)
    sys.exit(-20)
except tintri.TintriApiException as tae:
    print_error(tae.__str__())
    tintri.api_logout(server_name, session_id)
    sys.exit(-21)

# Logout
tintri.api_logout(server_name, session_id)
    
