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
from prettytable import PrettyTable

"""
 This Python script is responsible for creation of replication configuration.
 A user can make changes in the configuration section to change the configurations like debug mode.

 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage:
 a) ReplicationConfigurationClient <serverName> <userName> <password> <vmName> <sourceIp> <destinationIp> <displayName> <port> <passphrase> - Creates replication configuration for VM vmName

"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

##### ************** End of Configuration Section ************** ########


debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "
createReplicationPathFromCommandLine = False

if len(sys.argv) < 10:
    print(error_prefix+"Insufficient parameters passed for replication configuration creation")
    print(info_prefix+"COMMAND USAGE : ReplicationConfigurationClient serverName userName password vmName sourceIp destinationIp displayName port passphrase")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Create Replication Configuration ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
passWord = sys.argv[3]
vmName = sys.argv[4]
sourceIp = sys.argv[5]
destinationIp = sys.argv[6]
displayName = sys.argv[7]
port = sys.argv[8]
passphrase = sys.argv[9]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print(debug_prefix+"ServerName fetched : "+serverName)
    print(debug_prefix+"UserName fetched : "+userName)
    print(debug_prefix+"Password fetched : ********")
    print(debug_prefix+"VmName fetched : "+vmName)
    print(debug_prefix+"SourceIp : "+str(sourceIp))
    print(debug_prefix+"DestinationIp : "+str(destinationIp))
    print(debug_prefix+"Port : "+str(port))
    print(debug_prefix+"displayName : "+str(displayName))
    print(debug_prefix+"Passphrase : "+str(passphrase))
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


# Fetch VMs from VMStore
print()
print("STEP 2: Fetch all VMs from VMStore")


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

#Get VM Information by VM UUID

print()
print("STEP 3: Update the replication configuration for a particular VM")

if number_of_vms > 0:
    items = vms_paginated_result["items"]

    for count in range(0,number_of_vms):
        if vmName == items[count]["vmware"]["name"]:
            uuid = items[count]["uuid"]["uuid"]
            print(info_prefix+"Fetching information for VM with UUID: "+uuid+" for vmname : "+items[count]["vmware"]["name"])
            print()
            print("STEP 3: Add the replication configuration")
            #Payload, header and URL for creation of snapshot call
            throttle = {"typeId":"com.tintri.api.rest.v310.dto.domain.beans.repl.DatastoreReplicationPathThrottle","timeStart":"0 0 8 ? * mon-fri","timeEnd":"0 0 18 ? * mon-fri","throughputThrottledMbps":10,"throughputNonThrottledMbps":99999,"isEnabled":False}
            payloadCreationReplicationPath = {"sourceIp":sourceIp,"typeId":"com.tintri.api.rest.v310.dto.domain.beans.repl.DatastoreReplicationPath","destinationIp":destinationIp,"destinationPort":port,"destinationPassphrase":passphrase,"throttle":throttle,"displayName":displayName}
            payloadVmUUid = {"typeId": "com.tintri.api.rest.vcommon.dto.Uuid","entityTC": "VIRTUAL_MACHINE","uuid": uuid,"isPaused": False}
            payloadReplicationStats = {"typeId": "com.tintri.api.rest.v310.dto.domain.beans.perf.ReplicationStat","throughputLogicalMBps": 0,"throughputPhysicalMBps": 0,"bytesRemainingMB": 0}
            payloadCreationReplicationConfiguration={"typeId": "com.tintri.api.rest.v310.dto.domain.beans.repl.VirtualMachineReplicationConfig","vmUuid":payloadVmUUid,"isSource": True,"alertThresholdMinutes": 3000,"replicateParentsRequested": False,"isOneshot": False,"sourceIpAddress": "","isSystemDefault": False,"isDisabled": False,"tgcServiceGroupDefault": False, "stats": payloadReplicationStats, "path": payloadCreationReplicationPath}
            headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
            urlAddReplicationConfig = 'https://'+serverName+'/api/v310/vm/"+uuid+"/replicationConfig/'

            print(json.dumps(payloadCreationReplicationConfiguration))

            # Trying to create replication configuration from commandline parameters
            r = requests.post(urlAddReplicationConfig,json.dumps(payloadCreationReplicationConfiguration),headers=headers,verify=False)

            print("\t"+debug_prefix+"The HTTP Status code for adding replication configuration call to the server "+serverName + " is: "+str(r.status_code))

            if r.status_code is not 200:
                print("\t"+error_prefix+"The HTTP Status code for adding replication configuration call to the server is not 200")
                sys.exit(-9)

elif number_of_vms <= 0:
    print(error_prefix+"No VM's present on this server : "+serverName+" , hence we cannot create replication configuration")
    sys.exit(-1)

# Logout of VMStore

print()
print("STEP 4: Logout from VMStore")

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
print("**********End of Create Replication Configuration Sample Client Script**********")
