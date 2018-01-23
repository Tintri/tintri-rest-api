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

import requests
import json
import sys
import operator

"""
 This Python script is responsible for getting the list of VM's and showing it on console.
 A user can make changes in the configuration section to change the configurations like servername, username and password
 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: GetVmClient <serverName> <userName> <password>
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

##### ************** End of Configuration Section ************** ########

#### -----------Do not change anything below this section----------- #######

debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 4:
    print(error_prefix+"Insufficient parameters passed for getting VMs")
    print(info_prefix+"COMMAND USAGE : GetVmClient serverName userName password")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- GetVMs ------- "

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
    print(debug_prefix+"Going to make the Login call to server : "+serverName)
    print(debug_prefix+"The URL being used for login is : "+urlLogin)

try:
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
urlGetVM = 'https://'+serverName+'/api/v310/vm'

r = requests.get(urlGetVM,headers=headers, verify=False)


if debug_mode:
    print(debug_prefix+"The HTTP Status code for getVMs call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print(error_prefix+"The HTTP response for getVMs call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("The Json response of getVMs call to the server "+serverName+" is: "+r.text)

vms_paginated_result = json.loads(r.text)
number_of_vms = int(vms_paginated_result["filteredTotal"])
print(info_prefix+"Number of VMs fetched from getVMs call to the server "+serverName+" is : "+str(number_of_vms))

if number_of_vms > 10:
    print(info_prefix+"VM Names of first 10 VMs fetched : ")
    items = vms_paginated_result["items"]
    for count in range(0,10):
        print("\t"+str(count+1)+ ". "+items[count]["vmware"]["name"])
elif number_of_vms > 0 and number_of_vms < 10:
    print(info_prefix+"VM Name of first VM fetched : ")
    items = vms_paginated_result["items"]
    print("\t"+items[0]["vmware"]["name"])
elif number_of_vms == 0:
    print(info_prefix+"No VMs present")

#Get VM Information by VM UUID

print()
print("STEP 3: Show Information of a particular VM")

if number_of_vms > 0:
    items = vms_paginated_result["items"]
    print(info_prefix+"Fetching information for VM with UUID: "+items[0]["uuid"]["uuid"])
    #Header and URL for getVMs call
    headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
    urlGetVM_by_uuid = 'https://'+serverName+'/api/v310/vm/'+items[0]["uuid"]["uuid"]

    if debug_mode:
        print("The URL to get VM by VM UUid is: "+urlGetVM_by_uuid)
    r = requests.get(urlGetVM_by_uuid,headers=headers, verify=False)

    if debug_mode:
        print(debug_prefix+"The HTTP Status code for getVM by VM UUID call to the server "+serverName + " is: "+str(r.status_code))

    # if Http Response is not 200 then raise an exception
    if r.status_code is not 200:
        print(error_prefix+"The HTTP response for getVM by VM UUID call to the server "+serverName+" is not 200")
        sys.exit(-6)

    if debug_mode:
        print(debug_prefix+"The Json response of getVM by VM UUID call to the server "+serverName+" is: "+r.text)

    print(info_prefix+"The VM with name "+items[0]["vmware"]["name"]+" was last updated at "+items[0]["lastUpdatedTime"])


#Get Number of Deleted VMs

print()
print("STEP 4: Get Number of Deleted VMs")

#Header and URL for getVMs call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGet_deleted_VM = 'https://'+serverName+'/api/v310/vm?isDeleted=True'

r = requests.get(urlGet_deleted_VM,headers=headers, verify=False)

if debug_mode:
    print(debug_prefix+"The HTTP Status code for get deleted VMs call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print(error_prefix+"The HTTP response for get deleted VMs call to the server "+serverName+" is not 200")
    sys.exit(-6)

if debug_mode:
    print("The Json response of get deleted VMs call to the server "+serverName+" is: "+r.text)

vms__deleted_vm_paginated_result = json.loads(r.text)
number_of_deleted_vms = int(vms__deleted_vm_paginated_result["filteredTotal"])
print(info_prefix+"Number of deleted VMs fetched from getVms call to the server "+serverName+" is : "+str(number_of_deleted_vms))


# Logout of VMStore

print()
print("STEP 5: Logout from VMStore")

#Header and URL for getVMs call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetVM = 'https://'+serverName+'/api/v310/session/logout'
r = requests.get(urlGetVM,headers=headers, verify=False)

if debug_mode:
    print(debug_prefix+"The HTTP Status code for logout call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 204 then raise an exception
if r.status_code is not 204:
    print(error_prefix+"The HTTP response for logout call to the server "+serverName+" is not 204")
    sys.exit(-6)

print()
print("**********End of GetVM Sample Client Script**********")
