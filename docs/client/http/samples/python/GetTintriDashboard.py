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
 This Python script is responsible for getting the Dashboard information (Appliance info and Datastore stats) for
 VMstore and showing it on console.
 A user can make changes in the configuration section to change the configurations like debug_mode
 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: GetTintriDashboard <serverName> <userName> <password>
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

##### ************** End of Configuration Section ************** ########

debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 4:
    print(error_prefix+"Insufficient parameters passed for getting VMstore Dashboard info.")
    print(info_prefix+"COMMAND USAGE : GetTintriDashboard serverName userName password")
    sys.exit(-5)

header = "********************************* Tintri Ic. *********************************"
sub_heading = " ------- Get VMstore Dashboard info. ------- "

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

# Fetch Appliance info from VMStore
print()
print("STEP 2: Fetch and display Appliance info from VMStore")

#Header and URL for getApplianceInfo call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetApplianceInfo = 'https://'+serverName+'/api/v310/appliance/default/info'

print("\t"+info_prefix+"Fetching appliance info. by REST request: GET " + urlGetApplianceInfo)
r=requests.get(urlGetApplianceInfo,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getApplianceInfo call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getApplianceInfo call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getApplianceInfo call to the server "+serverName+" is: "+r.text)

#loads the appliance info result
applianceInfo_result = json.loads(r.text)

print()
#Printing appliance info. in tabular format
header = ['Serial No.', 'Model Name', 'Tintri OS version']
print("\t"+info_prefix+"---------- Appliance Information ----------")
x = PrettyTable(header)
row = [applianceInfo_result["serialNumber"], applianceInfo_result["modelName"], applianceInfo_result["osVersion"]]
x.add_row(row)
print(x)

print()
print("STEP 3: Fetch and display datastore stat from VMstore")

#Header and URL for getDatastoreInfo call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlDatastoreStat = 'https://'+serverName+'/api/v310/datastore/default/statsRealtime'

print("\t"+info_prefix+"Fetching Datastore stat by REST request: GET " + urlDatastoreStat)
r=requests.get(urlDatastoreStat,headers=headers, verify=False)

if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getDatastoreStat call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getDatastoreStat call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getDatastoreStat call to the server "+serverName+" is: "+r.text)

#loads the paginated result for datastore stats
datastoreStat_result = json.loads(r.text)

# get the filteredtotal number of datastore stats
number_of_dsStats=int(datastoreStat_result['filteredTotal'])
print()
#Printing datastore stat in tabular format
if number_of_dsStats > 0:
    print()
    header = ['Flash hit Ratio (%)', 'Network latency (ms)', 'Storage latency (ms)',
              'Disk latency (ms)', 'Host latency (ms)', 'Total latency (ms)',
              'Perf. Reserves allocated', 'Space used live Physical (GiB)', 'Space used other (GiB)',
              'Read IOPS', 'Write IOPS', 'Throughput Read (MBps)', 'Throughput Write (MBps)']
    stats = datastoreStat_result["items"][0]["sortedStats"]
    print("\t"+info_prefix+"---------- Datastore stats ----------")
    x = PrettyTable()
    x.add_column("Attributes", header)
    x.add_column("Values", [stats[0]["flashHitPercent"], stats[0]["latencyNetworkMs"],
                            stats[0]["latencyStorageMs"], stats[0]["latencyDiskMs"],
                            stats[0]["latencyHostMs"], stats[0]["latencyTotalMs"],
                            stats[0]["performanceReserveAutoAllocated"],
                            stats[0]["spaceUsedLivePhysicalGiB"],
                            stats[0]["spaceUsedOtherGiB"],
                            stats[0]["operationsReadIops"], stats[0]["operationsWriteIops"],
                            stats[0]["throughputReadMBps"], stats[0]["throughputWriteMBps"]
                            ]
    )
    print(x)

print()

# Logout of VMStore

print()
print("STEP 4: Logout from VMstore")

#Header and URL for logout call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
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
print("**********End of Get VMstore Dashboard Sample Client Script**********")

