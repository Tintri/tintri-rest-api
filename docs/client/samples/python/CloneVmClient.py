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
 This Python script is responsible for cloning a VM on VMstore.
 A user can make changes in the configuration section to change the configurations like debug_mode
 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: CloneVMClient <serverName> <userName> <password>
"""

##### ************** Utility Functions ************

def logout(): # Logout from VMstore function
    "Logs out from VMstore"
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
    print("**********End of Clone VM Sample Client Script**********")
    return

##### ************** End of Utility Functions ************



##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

##### ************** End of Configuration Section ************** ########

debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 4:
    print(error_prefix+"Insufficient parameters passed for Clone VM")
    print(info_prefix+"COMMAND USAGE : CloneVMClient serverName userName password")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Clone Virtual Machine on VMstore ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
password = sys.argv[3]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print(debug_prefix+"ServerName fetched : "+serverName)
    print(debug_prefix+"UserName fetched : "+userName)
    print(debug_prefix+"Password fetched : ********")
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

#Get all VMs and search for given VM from VMstore
print()
print("STEP 2: Fetch VM UUID for VM to clone")
print()

vmUuid = ""
input_vm_name = input("Please enter VM name to clone from: ")

print("Searching VM: " + input_vm_name + " on VMstore: " + serverName)

#Header and URL for getVMs call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}

#Get all Virtual Machines Request: GET https://<serverName>/api/v310/vm
urlGetVMs = 'https://'+serverName+'/api/v310/vm'

print("Fetching all VMs from VMstore through REST request: GET " + urlGetVMs)
r=requests.get(urlGetVMs,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getVMs call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getVMs call to the server "+serverName+" is not 200")
    sys.exit(-6)

if debug_mode:
    print("\t"+debug_prefix+"The Json response of getVMs call to the server "+serverName+" is: "+r.text)

#loads the paginated result for VMs
vms_paginated_result = json.loads(r.text)

# get the filteredtotal number of VMs
number_of_vms=int(vms_paginated_result['filteredTotal'])

if(number_of_vms > 0):
    print()
    print("\t"+info_prefix+"Number of VMs fetched from getVMs call to the server "
              +serverName+": "+str(number_of_vms))

    items = vms_paginated_result["items"]
    found = False
    for vm in items:
        if(vm["vmware"]["name"] == input_vm_name):
            vmUuid = vm["uuid"]["uuid"]
            found = True
            break

    if(found):
        print("\t"+info_prefix+"VM with name: '" + input_vm_name + "' has VM UUID: " + vmUuid)
    else:
        print("\t"+error_prefix+"VM with name: '" + input_vm_name + "' is not found on VMstore: " + serverName)
        print("\t"+error_prefix+"Clone VM operation can not be continued..")
        print()
        print("\t"+info_prefix+"Logout from VMstore")
        logout()
        exit(0)
else:
    print("\t"+error_prefix+"No VMs found on VMstore: " + serverName)
    print("\t"+error_prefix+"Clone VM operation can not be continued..")
    print()
    print("\t"+info_prefix+"Logout from VMstore")
    logout()
    exit(0)

print()
print("STEP 3: Accept and verify vCenter host name")
print()

vcenterHostName = ""
input_host_name = input("Please enter vCenter host name where cloned VM is to be hosted: ")

print("Verifying host: '" + input_host_name + "'")

#Header and URL for getHostResources call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}

#Get all host resources Request: GET https://<serverName>/api/v310/datastore/default/hostResources
urlGetHostResources = 'https://'+serverName+'/api/v310/datastore/default/hostResources'

print("Fetching host resources from VMstore through REST request: GET " + urlGetHostResources)
r=requests.get(urlGetHostResources,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getHostResources call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getHostResources call to the server "+serverName+" is not 200")
    sys.exit(-6)

if debug_mode:
    print("\t"+debug_prefix+"The Json response of getHostResources call to the server "+serverName+" is: "+r.text)

#loads the host resources result from VMstore
host_resources_result = json.loads(r.text)
found = False
if len(host_resources_result) > 0:
    for hostResource in host_resources_result:
        if(hostResource["hostname"] == input_host_name):
            vcenterHostName = input_host_name
            found = True
            break

    if(found):
        print("\t"+info_prefix+"vCenter host: '" + input_host_name + "' is valid.")
    else:
        print("\t"+error_prefix+"vCenter host: '" + input_host_name + "' is not connected with VMstore: " + serverName)
        print("\t"+error_prefix+"Please check the input host name.")
        print("\t"+error_prefix+"Clone VM operation can not be continued..")
        print()
        print("\t"+info_prefix+"Logout from VMstore")
        logout()
        exit(0)
else:
    print("\t"+error_prefix+"No host resource info found on VMstore: " + serverName)
    print("\t"+error_prefix+"Clone VM operation can not be continued..")
    print()
    print("\t"+info_prefix+"Logout from VMstore")
    logout()
    exit(0)

# Accept new cloned VM Name
print()
print("STEP 4: Accept new cloned VM name")
print()

cloneName = input("Please enter the name/prefix for clones: ")

# Accept clone count
print()
print("STEP 5: Accept clone count")
print()

cloneCount = input("Please enter clone count (number of clone copies): ")

# Submit clone VM task through REST request
print()
print("STEP 6: Clone VM (submit clone VM task on VMstore)")
print()

#Payload, header and URL for clone VM call
payload = {
   "typeId" : "com.tintri.api.rest.v310.dto.domain.beans.vm.VirtualMachineCloneSpec",
   "vmId" : vmUuid,
   "consistency" : "CRASH_CONSISTENT",
   "count" : str(cloneCount),
   "vmware": {
      "typeId" : "com.tintri.api.rest.v310.dto.domain.beans.vm.VirtualMachineCloneSpec$VMwareCloneInfo",
      "cloneVmName" : cloneName,
      "vCenterName" : vcenterHostName,
      "datastoreName" : "default"
   }
}
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}

#Clone VM Request: POST https://<serverName>/api/v310/vm
#payload = {
#   "typeId" : "com.tintri.api.rest.v310.dto.domain.beans.vm.VirtualMachineCloneSpec",
#   "vmId" : <VM Tintri UUID>,
#   "consistency" : "CRASH_CONSISTENT",
#   "count" : <Clone Count>,
#   "vmware": {
#      "typeId" : "com.tintri.api.rest.v310.dto.domain.beans.vm.VirtualMachineCloneSpec$VMwareCloneInfo",
#      "cloneVmName" : <Clone Name Prefix>,
#      "vCenterName" : <vCenter Host Name>,
#      "datastoreName" : "default"
#   }
#}
urlCloneVM = 'https://'+serverName+'/api/v310/vm'

print()

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the Clone VM call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for VM cloning is : "+urlCloneVM)

try:
    print("\t"+info_prefix+"Sending clone Request: POST " + urlCloneVM)
    r = requests.post(urlCloneVM, json.dumps(payload), headers=headers, verify=False)
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
    print("\t"+debug_prefix+"The HTTP Status code for Clone VM call to the server "+serverName + " is: "+str(r.status_code))

cloneSuccess = False
cloneTaskId = ""
# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for Clone VM call to the server "+serverName+" is not 200")
    if r.status_code == 500:
        clone_vm_result = json.loads(r.text)
        print("\t"+error_prefix+"Internal Server Error: Cause: " + clone_vm_result["causeDetails"])
    sys.exit(-6)
else:
    cloneSuccess = True
    print("\t"+info_prefix+"Successfully submitted clone VM task for VM: " + input_vm_name + " on VMstore: " + serverName)
    clone_vm_result = json.loads(r.text)
    cloneTaskId = clone_vm_result["uuid"]["uuid"]
    print("\t"+info_prefix+"Task ID for clone VM request: " + cloneTaskId)

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"The Json response of Clone VM call to the server "+serverName+" is: "+r.text)

# Check clone VM task status on VMstore
if(cloneSuccess):
    print()
    print("STEP 7: Check clone VM task status on VMstore")
    print()

    #Get Task Request: GET https://<serverName>/api/v310/task/<TaskUUID>
    urlGetCloneTask = 'https://'+serverName+'/api/v310/task/' + cloneTaskId
    pollCount = 1;
    taskStatus = "None"

    while(pollCount <= 10):
        time.sleep(2)

        print("Attempt: " + str(pollCount) + " - Polling status of Task with ID: " + cloneTaskId)
        r=requests.get(urlGetCloneTask,headers=headers, verify=False)

        if debug_mode:
            print("\t"+debug_prefix+"The HTTP Status code for getTask call to the server "+serverName + " is: "+str(r.status_code))

        # if Http Response is not 200 then raise an exception
        if r.status_code is not 200:
            print("\t"+error_prefix+"The HTTP response for getTask call to the server "+serverName+" is not 200")
            sys.exit(-6)

        if debug_mode:
            print("\t"+debug_prefix+"The Json response of getTask call to the server "+serverName+" is: "+r.text)

        #loads Task result for VMstore Task
        task_result = json.loads(r.text)
        taskStatus = task_result["state"]
        print("\t"+info_prefix+"Task Status: " + taskStatus)

        if(taskStatus == "SUCCESS"):
            print("\t"+info_prefix+"Successfully cloned VM: " + input_vm_name)
            break
        elif(taskStatus == "FAILED"):
            print("\t"+error_prefix+"Failed to clone VM: " + input_vm_name)
            break

# Logout of VMStore
print()
print("STEP 8: Logout from VMstore")
logout()
