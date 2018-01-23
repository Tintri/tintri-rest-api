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
 This Python script is responsible for getting the list of VM snapshots and showing it on console.
 A user can make changes in the configuration section to change the configurations like debug_mode
 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: GetVmSnapshotClient <serverName> <userName> <password>
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

# var fo display number of snapshot on console
number_of_items_to_be_displayed_on_console = 10

##### ************** End of Configuration Section ************** ########

debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 4:
    print(error_prefix+"Insufficient parameters passed for getting VMs")
    print(info_prefix+"COMMAND USAGE : GetVmClient serverName userName password")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Get VM Snapshots ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
passWord = sys.argv[3]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print(debug_prefix+"ServerName fetched : "+serverName)
    print(debug_prefix+"UserName fetched : "+userName)
    print(debug_prefix+"Password fetched : ********")
    print()

# Login to VMStore

#Payload, header and URL for login call
payload = {"newPassword": None, "username": userName, "roles": None, "password": passWord, "typeId": "com.tintri.api.rest.vcommon.dto.rbac.RestApiCredentials"}
headers = {'content-type': 'application/json'}
urlLogin = 'https://'+serverName+'/api/v310/session/login'

print()
print(header)
print()
print(sub_heading)
print()
print("SERVER NAME : "+serverName)
print()
print("STEP 1: Login to VMStore")

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the Login call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for login is : "+urlLogin)

try:
    # Trying to login to the vmstore (POST request)
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

# Fetch VM snapshots from VMStore
print()
print("STEP 2: Fetch VM snapshots from VMStore")

#Header and URL for getSnapshot call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetVMSnapshots = 'https://'+serverName+'/api/v310/snapshot'

# Trying to fetch VM Snapshots from vmstore (GET request)
r=requests.get(urlGetVMSnapshots,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getSnapshots call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getSnapshots call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getSnapshots call to the server "+serverName+" is: "+r.text)

#loads the paginated result for snapshots
vmsnapshots_paginated_result = json.loads(r.text)

# get the filteredtotal number of snapshots

number_of_vmsnapshots=int(vmsnapshots_paginated_result['filteredTotal'])
print()
print("\t"+info_prefix+"Number of VM snapshots fetched from getSnapshots call to the server "+serverName+" is : "+str(number_of_vmsnapshots))
#printing first 10 vm snapshot on consoles
if number_of_vmsnapshots > number_of_items_to_be_displayed_on_console:
    header = ['No.', 'Source VM', 'Creation Date', 'Description']
    print("\t"+info_prefix+"List of first "+str(number_of_items_to_be_displayed_on_console)+" snapshots:---")
    items = vmsnapshots_paginated_result["items"]
    x = PrettyTable(header)
    for count in range(0,number_of_items_to_be_displayed_on_console):
        row = [str(count+1),items[count]["vmName"],time.ctime(int(items[count]["createTime"]/1000)),items[count]["description"]]
        x.add_row(row)
    print(x)

elif number_of_vmsnapshots > 0 and number_of_vmsnapshots < number_of_items_to_be_displayed_on_console:
    print(info_prefix+"VM snapshots description of first VM fetched : ")
    items = vmsnapshots_paginated_result["items"]
    print("\t"+items[0])
elif number_of_vmsnapshots == 0:
    print(info_prefix+"No VM snapshots are present")

print()
print("STEP 3: Show Information of a particular VM snapshot")
print()
if number_of_vmsnapshots > 0:
    items = vmsnapshots_paginated_result["items"]
    print("\t"+info_prefix+"Fetching information for VM snapshot with snapshot UUID: "+items[0]["uuid"]["uuid"])
    #Header and URL for getSnapshot call
    headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
    urlGetVMSnapshots_by_uuid = 'https://'+serverName+'/api/v310/snapshot/'+items[0]["uuid"]["uuid"]

    if debug_mode:
        print("\t"+debug_prefix+"The URL to get VM snapshot by snapshot UUid is: "+urlGetVMSnapshots_by_uuid)
    r = requests.get(urlGetVMSnapshots_by_uuid,headers=headers, verify=False)

    if debug_mode:
        print("\t"+debug_prefix+"The HTTP Status code for getSnapshot by Snapshot UUID call to the server "+serverName + " is: "+str(r.status_code))

    # if Http Response is not 200 then raise an exception
    if r.status_code is not 200:
        print("\t"+error_prefix+"The HTTP response for getSnapshot by Snapshot UUID call to the server "+serverName+" is not 200")
        sys.exit(-6)

    if debug_mode:
        print("\t"+debug_prefix+"The Json response of getSnapshot by snapshot UUID call to the server "+serverName+" is: "+r.text)

    print("\t"+info_prefix+"The snapshot with Source VM "+items[0]["vmName"]+" was last updated at "+items[0]["lastUpdatedTime"])
# Logout of VMStore

print()
print("STEP 4: Logout from VMStore")

#Header and URL for getVMs call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
url_VMStore_logout = 'https://'+serverName+'/api/v310/session/logout'

if debug_mode:
    print("\t"+debug_prefix+"The URL being used for logout is : "+url_VMStore_logout)

# Trying to logout from vmstore (GET request)
r = requests.get(url_VMStore_logout,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for logout call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 204 then raise an exception
if r.status_code is not 204:
    print("\t"+error_prefix+"The HTTP response for logout call to the server "+serverName+" is not 204")
    sys.exit(-6)

print()
print("**********End of Get VM Snapshots Sample Client Script**********")

