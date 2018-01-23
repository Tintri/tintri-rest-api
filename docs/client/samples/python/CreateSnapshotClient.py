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
from pip._vendor.distlib.compat import raw_input

import requests
import json
import sys

"""
 This Python script is responsible for creation of snapshot.
 A user can make changes in the configuration section to change the configurations like debug mode.

 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: CreateSnapshotClient <serverName> <userName> <password> <snapshotName>

 NOTE: Do not use spaces in snapshotName
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

##### ************** End of Configuration Section ************** ########


debug_prefix = "[DEBUG] : "
info_prefix  = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 5:
    print(error_prefix+"Insufficient parameters passed for creating snapshot")
    print(info_prefix+"COMMAND USAGE : CreateSnapshotClient serverName userName password snapshotName")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Create Snapshot ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
passWord = sys.argv[3]
snapshotName = sys.argv[4]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print(debug_prefix+"ServerName fetched : "+serverName)
    print(debug_prefix+"UserName fetched : "+userName)
    print(debug_prefix+"Password fetched : ********")
    print(debug_prefix+"Snapshot Name fetched : "+snapshotName)
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
    print(debug_prefix+"Going to make the Login call to server : "+serverName)
    print(debug_prefix+"The URL being used for login is : "+urlLogin)

try:
    # Trying to login to the vmstore (POST request)
    r = requests.post(urlLogin, json.dumps(payload), headers=headers, verify=False)
except requests.ConnectionError:
    print(error_prefix+"API Connection error occurred")
    sys.exit(-1)
except requests.HTTPError:
    print(error_prefix+"HTTP error occurred")
    sys.exit(-2)
except requests.Timeout:
    print(error_prefix+"Request timed out")
    sys.exit(-3)
except Exception:
    print(error_prefix+"An unexpected error occurred")
    sys.exit(-4)

if debug_mode:
    print(debug_prefix+"The HTTP Status code for login call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print(error_prefix+"The HTTP response for login call to the server "+serverName+" is not 200")
    sys.exit(-6)

# Debug Logs to console
if debug_mode:
   print(debug_prefix+"The Json response of login call to the server "+serverName+" is: "+r.text)

# Fetch SessionId from Cookie
session_id = r.cookies['JSESSIONID']


# Fetch VMs from VMStore
print()
print("STEP 2: Fetch VMs from VMStore")


#Header and URL for getVMs call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
# Trying to fetch list of VMs (GET request)
urlGetVM = 'https://'+serverName+'/api/v310/vm'

r = requests.get(urlGetVM,headers=headers, verify=False)


if debug_mode:
    print(debug_prefix+"The HTTP Status code for getVMs call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print(error_prefix+"The HTTP response for getVMs call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print(debug_prefix+"The Json response of getVMs call to the server "+serverName+" is: "+r.text)

vms_paginated_result = json.loads(r.text)
number_of_vms = int(vms_paginated_result["filteredTotal"])
print(info_prefix+"Number of VMs fetched from getVMs call to the server "+serverName+" is : "+str(number_of_vms))

if   number_of_vms > 0:
    items = vms_paginated_result["items"]
    finalVm = None
    index = -1

    # Iterate through all VM's and search for a VM with flag isLive set to true, since snapshot can be created only on the same
    for count in range(0,number_of_vms):
        isLive = items[count]["isLive"]
        if isLive == True:
            index = count
            break

    if index >= 0:
        finalVm = items[index]
        vmUuid = finalVm["uuid"]["uuid"]
        vmName = finalVm["vmware"]["name"]
        print(info_prefix+"Going to create snapshot for VM:- "+vmName+" and uuid :-"+vmUuid)

elif number_of_vms == 0:
    print(info_prefix+"No VMs present")
    print(error_prefix+"Cannot create snapshot since no VM's present on this vmstore")
    sys.exit(-7)


if finalVm == None:
    print(error_prefix+" Cannot create snapshot since, there is no VM present with isLive flag set to true")
    sys.exit(-8)

#Payload, header and URL for creation of snapshot call
payloadCreationSnapshot =
    [{"retentionMinutes": 120,
      "typeId": "com.tintri.api.rest.v310.dto.domain.beans.snapshot.SnapshotSpec",
      "snapshotName": snapshotName,
      "sourceVmTintriUUID": vmUuid,
      "replicaRetentionMinutes": 120,
      "consistency": "CRASH_CONSISTENT"
    }]
headers =
    {'content-type': 'application/json',
     'cookie': 'JSESSIONID='+session_id
    }
urlCreationSnaphot = 'https://'+serverName+'/api/v310/snapshot'

try:
    # Trying to create snapshot (POST request)
    r = requests.post(urlCreationSnaphot, json.dumps(payloadCreationSnapshot), headers=headers, verify=False)
except requests.ConnectionError:
    print(error_prefix+"API Connection error occurred")
    sys.exit(-1)
except requests.HTTPError:
    print(error_prefix+"HTTP error occurred")
    sys.exit(-2)
except requests.Timeout:
    print(error_prefix+"Request timed out")
    sys.exit(-3)
except Exception:
    print(error_prefix+"An unexpected error occurred")
    sys.exit(-4)

if debug_mode:
    print(debug_prefix+"The HTTP Status code for creation of snapshot to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print(error_prefix+"The HTTP response for login call to the server "+serverName+" is not 200")
else:
    print(info_prefix+"Successfully created snapshot : "+ snapshotName+ " on sourceVm : "+vmName)


# Logout of VMStore

print()
print("STEP 3: Logout from VMStore")

#Header and URL for Logout from VMStore
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlVmStoreLogout = 'https://'+serverName+'/api/v310/session/logout'
# Trying to logout from vmstore (GET request)
r = requests.get(urlVmStoreLogout,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for logout call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 204 then raise an exception
if r.status_code is not 204:
    print("\t"+error_prefix+"The HTTP response for logout call to the server "+serverName+" is not 204")
    sys.exit(-6)

print()
print("**********End of Create Snapshot Sample Client Script**********")
