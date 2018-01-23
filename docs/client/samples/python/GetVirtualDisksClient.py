#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The code example provided here is for reference only to illustrate
# sample workflows and may not be appropriate for use in actual operating
# environments. 
# Support will be provided by Tintri for the Tintri APIs, but theses
# examples are for illustrative purposes only and are not supported.
# Tintri is not responsible for any outcome resulting from the use
# of these scripts.
# 
from datetime import date, datetime

import requests
import json
import sys
import time
from prettytable import PrettyTable

"""
 This Python script is responsible for getting the list of virtual disks for VMs on VMstore and showing it on console.
 A user can make changes in the configuration section to change the configurations like debug_mode
 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: GetVirtualDisksClient <serverName> <userName> <password> <VM_Name>
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

# var for display number of Virtual Disks on console
page_size = 10

##### ************** End of Configuration Section ************** ########

debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 5:
    print(error_prefix+"Insufficient parameters passed for getting Virtual Disks")
    print(info_prefix+"COMMAND USAGE : GetVirtualDisksClient serverName userName password VM_Name")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Get Virtual Disks of VMs on VMstore ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
password = sys.argv[3]
vmName = sys.argv[4]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print(debug_prefix+"ServerName fetched : "+serverName)
    print(debug_prefix+"UserName fetched : "+userName)
    print(debug_prefix+"Password fetched : ********")
    print(debug_prefix+"VM Name fetched : " + vmName)
    print()

# Login to VMstore

#Payload, header and URL for login call
payload = {"newPassword": None, "username": userName, "roles": None, "password": password, "typeId": "com.tintri.api.rest.vcommon.dto.rbac.RestApiCredentials"}
headers = {'content-type': 'application/json'}

#Login Request: POST https://<serverName>/api/v310/session/login
#Payload JSON:
#   {
#       "newPassword": None,
#       "username": <userName>,
#       "roles": None,
#       "password": <password>,
#       "typeId": "com.tintri.api.rest.vcommon.dto.rbac.RestApiCredentials"
#   }
urlLogin = 'https://'+serverName+'/api/v310/session/login'

print()
print(header)
print()
print(sub_heading)
print()
print("SERVER NAME : "+serverName)
print()
print("STEP 1: Login to VMstore")

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the Login call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for login is : "+urlLogin)

try:
    r = requests.post(urlLogin, json.dumps(payload), headers=headers, verify=False)
except requests.ConnectionError:
    print("\t"+error_prefix+"API Connection error occurred")
    sys.exit(-1)
except requests.HTTPError:
    print("\t"+error_prefix+"HTTP error occurred")
    sys.exit(-2)
except requests.Timeout:
    print("\t"+error_prefix+"Request timed out")
    sys.exit(-3)
except Exception:
    print("\t"+error_prefix+"An unexpected error occurred")
    sys.exit(-4)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for login call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for login call to the server "+serverName+" is not 200")
    sys.exit(-6)

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"The Json response of login call to the server "+serverName+" is: "+r.text)

# Fetch SessionId from Cookie
session_id = r.cookies['JSESSIONID']

#Get all Virtual Disks from VMstore
print()
print("STEP 2: Fetch information of all Virtual Disks")
print()

#Header and URL for getVirtualDisks call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}

#Get all Virtual Disks Request: GET https://<serverName>/api/v310/virtualDisk
urlGetVDisks = 'https://'+serverName+'/api/v310/virtualDisk'

print("Fetching all Virtual Disks from VMstore through REST request: GET " + urlGetVDisks)
r=requests.get(urlGetVDisks,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getVirtualDisks call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getVirtualDisks call to the server "+serverName+" is not 200")
    sys.exit(-6)

if debug_mode:
    print("\t"+debug_prefix+"The Json response of getVirtualDisks call to the server "+serverName+" is: "+r.text)

#loads the paginated result for Virtual Disks
vdisks_paginated_result = json.loads(r.text)

# get the filteredtotal number of Virtual Disks
number_of_vdisks=int(vdisks_paginated_result['filteredTotal'])

print()
print("\t"+info_prefix+"Number of Virtual Disks fetched from getVirtualDisks call to the server "
          +serverName+": "+str(number_of_vdisks))

print()
print("STEP 3: Show Information of all Virtual Disks for given VM: '" + vmName + "'")
print()
if number_of_vdisks > 0:
    count = 0
    header = ['No.', 'VM', 'VM UUID', 'VDisk Name', 'Instance UUID']
    items = vdisks_paginated_result["items"]
    x = PrettyTable(header)
    for vDisk in items:
        if(vDisk["vmName"] == vmName):
            count = count + 1
            row = [str(count), vDisk["vmName"], vDisk["vmUuid"]["uuid"], vDisk["name"],vDisk["instanceUuid"]]
            x.add_row(row)

    if len(x._rows) < 1:
        print("\t"+info_prefix+"No Virtual Disks found for VM: '" + vmName + "'")
    else:
        print("\t"+info_prefix+"---- List of Virtual Disks for VM : '" + vmName + "' ----")
        print(x)

# Fetch Paginated result of Virtual Disks from VMStore
print()
print("STEP 4: Fetch Paginated result of all Virtual Disks from VMStore")
print()
number_of_pages = 0
if(number_of_vdisks > 0):
    if(number_of_vdisks % page_size == 0):
        number_of_pages = int(number_of_vdisks / page_size)
    else:
        number_of_pages = int((number_of_vdisks + page_size) / page_size)
    print()
    print("\t"+info_prefix+"Total number of Virtual Disks available on the server "
          +serverName+": "+str(number_of_vdisks) + ", spanning " + str(number_of_pages) + " pages with page size: "
          + str(page_size) + ".")

    print()
    input_char = raw_input("Continue with paginated results (y/n)?: ")
    if (input_char == 'y' or input_char == 'Y'):
        #printing paginated list of Virtual Disk Records on console
        header = ['No.', 'VM', 'VM UUID', 'VDisk Name', 'Instance UUID']

        offset = 0
        page_number = 1
        while (page_number <= number_of_pages):
            #Virtual Disk Pagination Request: GET https://<serverName>/api/v310/virtualDisk?offset=<int_offset>&limit=<int_page_size>
            urlGetVDisks = 'https://'+serverName+'/api/v310/virtualDisk?offset=' + str(offset) \
                       + '&limit=' + str(page_size)
            print("Virtual disk pagination REST request: GET " + urlGetVDisks)
            r=requests.get(urlGetVDisks,headers=headers, verify=False)

            if debug_mode:
                print("\t"+debug_prefix+"The HTTP Status code for getPaginatedVirtualDisks call to the server "+serverName + " is: "+str(r.status_code))

            # if Http Response is not 200 then raise an exception
            if r.status_code is not 200:
                print("\t"+error_prefix+"The HTTP response for getPaginatedVirtualDisks call to the server "+serverName+" is not 200")
                sys.exit(-6)

            if debug_mode:
                print("\t"+debug_prefix+"The Json response of getPaginatedVirtualDisks call to the server "+serverName+" is: "+r.text)

            #loads the paginated result for Virtual Disks
            vdisks_paginated_result = json.loads(r.text)

            items = vdisks_paginated_result["items"]
            page_offset = 0
            total_items_curr_page = len(items)
            x = PrettyTable(header)
            while(page_offset < total_items_curr_page):
                row = [str(offset + page_offset + 1), items[page_offset]["vmName"],
                       items[page_offset]["vmUuid"]["uuid"], items[page_offset]["name"],items[page_offset]["instanceUuid"]]
                x.add_row(row)
                page_offset = page_offset + 1

            print()
            print("\t"+info_prefix+"List of Virtual Disks ---- Page: " + str(page_number) + "/" + str(number_of_pages)
                  + "(#Disks " + str(offset + 1) + " to " + str(offset + len(items)) + ").")
            print(x)

            page_number = page_number + 1
            offset = offset + page_size

            if(page_number <= number_of_pages):
                print()
                go_to_next = raw_input("Go to next page (y/n)?: ")
                if(go_to_next != 'y' and go_to_next != 'Y'):
                    break
    else:
        print()
        print("Skipping Virtual Disk pagination..")
else:
    print(info_prefix+"No Virtual Disks are present on VMstore: " + serverName)


# Logout of VMStore
print()
print("STEP 5: Logout from VMstore")

#Header and URL for logout call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
#VMstore Logout Request: GET https://<serverName>/api/v310/session/logout
url_VMStore_logout = 'https://'+serverName+'/api/v310/session/logout'

if debug_mode:
    print("\t"+debug_prefix+"The URL being used for logout is : "+url_VMStore_logout)

r = requests.get(url_VMStore_logout,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for logout call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 204 then raise an exception
if r.status_code is not 204:
    print("\t"+error_prefix+"The HTTP response for logout call to the server "+serverName+" is not 204")
    sys.exit(-6)

print()
print("**********End of Get Virtual Disks Sample Client Script**********")

