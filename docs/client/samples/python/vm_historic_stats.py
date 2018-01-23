#!/usr/bin/env/python
# -*- coding: utf-8 -*-
#
# The code example provided here is for reference only to illustrate
# sample workflows and may not be appropriate for use in actual operating
# environments. 
# Support will be provided by Tintri for the Tintri APIs, but theses
# examples are for illustrative purposes only and are not supported.
# Tintri is not responsible for any outcome resulting for the use
# of these scripts.
# 

import requests
import json
import sys
import tintri
import pprint
from types import *
from datetime import datetime


"""
 This Python script compares vm stats

 Command usage: 

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

def print_stats(paged_result, count):
    page = paged_result["page"]
    page_total = paged_result["pageTotal"]
    print_info("Page " + str(page) + " of " + str(page_total))

    items = paged_result["items"]
    #print_info("items: " + str(items))
    for stat in items:
        num_slices = stat["numberOfSlices"]
        start_time = stat["startTime"]
        print_info(start_time + " with " + str(num_slices) + " slices")

        historic_stat = stat["sortedStats"]
        #space_used = historic_stat["spaceUsedGiB"]
        print(str(count) + ": " + start_time )
        count += 1

    return count
    
# main
if len(sys.argv) < 4:
    print("\nCollect VM historic status")
    print("Usage: " + sys.argv[0] + " server_name user_name password <page_size>\n")
    sys.exit(-1)

server_name = sys.argv[1]
user_name = sys.argv[2]
password = sys.argv[3]
page_size = 25  # init default
if len(sys.argv) == 5:
    page_size = sys.argv[4]

# Get the preferred version
r = tintri.api_get(server_name, '/info')
if r.status_code != 200:
    print_error("The HTTP response for the get invoke to the server " +
          server_name + " is not 200, but is: " + str(r.status_code))
    print_error("URL = /api/info")
    print_error("response: " + r.text)
    sys.exit(-2)

json_info = r.json()

print_info("API Version: " + json_info['preferredVersion'])

# Login to VMstore
session_id = tintri.api_login(server_name, user_name, password)

# Get a VM to work with
p_filter = {'limit'  : 1,
            'sortedBy' : 'LATENCY',
            'sortOrder' : 'DESC',
            'live'   : "TRUE"}
url = "/v310/vm"
r = tintri.api_get_query(server_name, url, p_filter, session_id)
if r.status_code != 200:
    print_error("The HTTP response for the get invoke to the server " +
          server_name + " is not 200, but is: " + str(r.status_code))
    print_error("URL = " + url)
    print_error("response: " + r.text)
    tintri.api_logout(server_name, session_id)
    sys.exit(-10)

vm_paginated_result = r.json()
items = vm_paginated_result['items']
vm = items[0]
vm_uuid = vm['uuid']['uuid']
vm_name = vm['vmware']['name']
print_info("VM: " + vm_name + " : " + vm_uuid + " " + str(vm['isLive']))

# Create filter to get the oldest user generated snapshot
q_filter = {#'queryType': 'TOP_DOCS_BY_LATEST_TIME',
            'since'    : '2015-03-11T15:00:00.915-08:00',
            'offset'   : 0,
            'limit'    : page_size }

# Get historic stats
count = 1
historic_url = "/v310/vm/" + vm_uuid + "/statsHistoric"
print_info("URL: " + historic_url + ", " + str(q_filter))
r = tintri.api_get_query(server_name, historic_url, q_filter, session_id)

print_debug("The JSON response of the get invoke to the server " +
            server_name + " is: " + r.text)
    
# if HTTP Response is not 200 then raise an error
if r.status_code != 200:
    print_error("The HTTP response for the get invoke to the server " +
          server_name + " is not 200, but is: " + str(r.status_code))
    print_error("URL = " + historic_url)
    print_error("response: " + r.text)
    tintri.api_logout(server_name, session_id)
    sys.exit(-10)

historic_paginated_result = r.json()
print_info("Absolute Total: " + str(historic_paginated_result["absoluteTotal"]))

count = print_stats(historic_paginated_result, count)
print_info("limit: " + str(historic_paginated_result['limit']))

# While there are more Vms, go get them
while 'next' in historic_paginated_result:
    url = historic_url + "?" + historic_paginated_result['next']
    print_info("Next GET URL: " + str(count) + ": " + url)

    r = tintri.api_get(server_name, url, session_id)

    historic_result = r.json()
    count = print_stats(historic_paginated_result, count)

# Logout
tintri.api_logout(server_name, session_id)

