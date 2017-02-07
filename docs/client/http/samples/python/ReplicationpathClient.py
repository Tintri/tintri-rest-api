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
 This Python script is responsible for creation of replication path.
 A user can make changes in the configuration section to change the configurations like debug mode.

 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage:
 a) ReplicationpathClient <serverName> <userName> <password> - Fetches the existing replication paths; deletes them and recreate the path
 b) ReplicationpathClient <serverName> <userName> <password> <sourceIp> <destinationIp> <displayName> <port> <passphrase> - Creates replication path


 NOTE: Do not use spaces in snapshotName
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

##### ************** End of Configuration Section ************** ########


debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "
createReplicationPathFromCommandLine = False

if len(sys.argv) < 4:
    print(error_prefix+"Insufficient parameters passed for creating replication path")
    print(info_prefix+"COMMAND USAGE : ReplicationpathClient serverName userName password")
    sys.exit(-5)
elif len(sys.argv) > 4 and len(sys.argv) < 9:
    print(error_prefix+"Insufficient parameters passed for replication path creation")
    print(info_prefix+"COMMAND USAGE : ReplicationpathClient serverName userName password sourceIp destinationIp displayName port passphrase")
    sys.exit(-5)
elif len(sys.argv) == 4:
    createReplicationPathFromCommandLine = False
elif len(sys.argv) == 9:
    createReplicationPathFromCommandLine = True

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Create Replication Path ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
passWord = sys.argv[3]
sourceIp = None
destinationIp = None
port = -1
passphrase = None
displayName = None

if(createReplicationPathFromCommandLine):
    sourceIp = sys.argv[4]
    destinationIp = sys.argv[5]
    displayName = sys.argv[6]
    port = sys.argv[7]
    passphrase = sys.argv[8]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print(debug_prefix+"ServerName fetched : "+serverName)
    print(debug_prefix+"UserName fetched : "+userName)
    print(debug_prefix+"Password fetched : ********")
    print(debug_prefix+"SourceIp : "+sourceIp)
    print(debug_prefix+"DestinationIp : "+destinationIp)
    print(debug_prefix+"Port : "+port)
    print(debug_prefix+"displayName : "+displayName)
    print(debug_prefix+"Passphrase : "+passphrase)
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


# Get all the replication Paths configured

print()
print("STEP 2: Fetch all replication Paths configured")
#Header and URL for Logout from VMStore
headersFetchReplicationPath = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlFetchReplicationPath = 'https://'+serverName+'/api/v310/datastore/default/replicationPath'

# Trying to fetch all replication paths configured (GET request)
r = requests.get(urlFetchReplicationPath,headers=headersFetchReplicationPath, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getReplPaths call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getReplPaths call to the server "+serverName+" is not 200")
    sys.exit(-6)

if debug_mode:
    print("\t"+debug_prefix+"The Json response of getReplPaths call to the server "+serverName+" is: "+r.text)

json_response_repl_paths = json.loads(r.text)
table_header = ['No.', 'Source IP', 'Destination IP', 'Destination Passphrase']
x = PrettyTable(table_header)
number_of_repl_paths = len(json_response_repl_paths)

for count in range(0,number_of_repl_paths):
    row = [str(count+1),json_response_repl_paths[count]["sourceIp"],json_response_repl_paths[count]["destinationIp"],json_response_repl_paths[count]["destinationPassphrase"]]
    x.add_row(row)
print(x)

# Fetch one of the replPaths and delete it, if there are existing
if number_of_repl_paths > 0 and createReplicationPathFromCommandLine == False:
    print()
    print("STEP 3: Delete one of the existing replication paths")
    sourceIpToDelete = json_response_repl_paths[0]["sourceIp"]
    destinationIpToDelete = json_response_repl_paths[0]["destinationIp"]
    passphraseToDelete = json_response_repl_paths[0]["destinationPassphrase"]
    replinkId = json_response_repl_paths[0]["id"]
    throttle = json_response_repl_paths[0]["throttle"]
    destinationPort = json_response_repl_paths[0]["destinationPort"]
    displayName = json_response_repl_paths[0]["displayName"]
    internalId = json_response_repl_paths[0]["internalId"]

    if debug_mode:
        print("\t"+debug_prefix+"sourceIpToDelete : "+sourceIpToDelete)
        print("\t"+debug_prefix+"destinationIpToDelete : "+destinationIpToDelete)
        print("\t"+debug_prefix+"passphraseToDelete : "+passphraseToDelete)
        print("\t"+debug_prefix+"replicationLinkId : "+replinkId)
        print("\t"+debug_prefix+"throttle : "+str(throttle))
        print("\t"+debug_prefix+"destinationPort : "+str(destinationPort))
        print("\t"+debug_prefix+"displayName : "+str(displayName))
        print("\t"+debug_prefix+"internalId : "+str(internalId))

    #Header and URL for deleting existing replication path from VMStore
    headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
    urlDeleteReplicationPath = 'https://'+serverName+'/api/v310/datastore/default/replicationPath/'+str(replinkId)

    if debug_mode:
        print("\t"+debug_prefix+"URL for deleting existing replication path is : "+urlDeleteReplicationPath)

    r = requests.delete(urlDeleteReplicationPath,headers=headers,verify=False)

    if debug_mode:
        print("\t"+debug_prefix+"The HTTP Status code for deleting existing replication path call to the server "+serverName + " is: "+str(r.status_code))

    if r.status_code is not 200:
        json_response_repl_paths_delete = json.loads(r.text)
        print("\t"+error_prefix+"The reason for failure of deletion of existing replication path on the server "+serverName + " is : \n"+str(json_response_repl_paths_delete["message"]))
        sys.exit(-9)

    #Payload, header and URL for creation of snapshot call
    payloadCreationReplicationPath = {"sourceIp":sourceIpToDelete,"typeId":"com.tintri.api.rest.v310.dto.domain.beans.repl.DatastoreReplicationPath","destinationIp":destinationIpToDelete,"destinationPort":destinationPort,"destinationPassphrase":passphraseToDelete,"throttle":throttle,"displayName":displayName,"id":replinkId,"internalId":internalId}
    headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
    urlAddReplicationPath = 'https://'+serverName+'/api/v310/datastore/default/replicationPath/'

    r = requests.post(urlAddReplicationPath,headers=headers,verify=False)

    if debug_mode:
        print("\t"+debug_prefix+"The HTTP Status code for adding replication path call to the server "+serverName + " is: "+str(r.status_code))

    if r.status_code is not 200:
        print("\t"+error_prefix+"The HTTP Status code for adding replication path call to the server is not 200")
        sys.exit(-9)

elif number_of_repl_paths == 0 and createReplicationPathFromCommandLine == False:
    print()
    print(error_prefix+"Either there are no existing replication paths available or no parameters passed to create a new replication path")
    sys.exit(-9)
elif createReplicationPathFromCommandLine == True:
    print()
    print("STEP 3: Add the replication path")
    #Payload, header and URL for creation of snapshot call
    throttle = {"typeId":"com.tintri.api.rest.v310.dto.domain.beans.repl.DatastoreReplicationPathThrottle","timeStart":"0 0 8 ? * mon-fri","timeEnd":"0 0 18 ? * mon-fri","throughputThrottledMbps":10,"throughputNonThrottledMbps":99999,"isEnabled":False}
    payloadCreationReplicationPath = {"sourceIp":sourceIp,"typeId":"com.tintri.api.rest.v310.dto.domain.beans.repl.DatastoreReplicationPath","destinationIp":destinationIp,"destinationPort":port,"destinationPassphrase":passphrase,"throttle":throttle,"displayName":displayName}
    headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
    urlAddReplicationPath = 'https://'+serverName+'/api/v310/datastore/default/replicationPath/'

    # Trying to create replication path from commandline parameters
    r = requests.post(urlAddReplicationPath,json.dumps(payloadCreationReplicationPath),headers=headers,verify=False)

    if debug_mode:
        print("\t"+debug_prefix+"The HTTP Status code for adding replication path call to the server "+serverName + " is: "+str(r.status_code))

    if r.status_code is not 200:
        print("\t"+error_prefix+"The HTTP Status code for adding replication path call to the server is not 200")
        sys.exit(-9)


# Get all the replication Paths configured

print()
print("STEP 4: Fetch all replication Paths configured after addition of new replication path")
#Header and URL for Logout from VMStore
headersFetchReplicationPath = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlFetchReplicationPath = 'https://'+serverName+'/api/v310/datastore/default/replicationPath'

# Trying to fetch all replication paths configured (GET request)
r = requests.get(urlFetchReplicationPath,headers=headersFetchReplicationPath, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getReplPaths call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getReplPaths call to the server "+serverName+" is not 200")
    sys.exit(-6)

if debug_mode:
    print("\t"+debug_prefix+"The Json response of getReplPaths call to the server "+serverName+" is: "+r.text)

json_response_repl_paths = json.loads(r.text)
table_header = ['No.', 'Source IP', 'Destination IP', 'Destination Passphrase']
x = PrettyTable(table_header)
number_of_repl_paths = len(json_response_repl_paths)

for count in range(0,number_of_repl_paths):
    row = [str(count+1),json_response_repl_paths[count]["sourceIp"],json_response_repl_paths[count]["destinationIp"],json_response_repl_paths[count]["destinationPassphrase"]]
    x.add_row(row)
print(x)


# Logout of VMStore

print()
print("STEP 5: Logout from VMStore")

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
print("**********End of Create Replication Path Sample Client Script**********")
