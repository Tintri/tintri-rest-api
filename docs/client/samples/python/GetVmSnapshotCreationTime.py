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
import time
import sys
from prettytable import PrettyTable
from datetime import datetime

"""
 This Python script is responsible for getting the list of latest snapshot
 creation time stamps for all VMs on the Tintri appliance.
 A user can make changes in the configuration section to change the
 configurations like debug_mode.
 if debug_mode is set to False, then the JSON response won't be printed on
 the console.
 Command usage: GetVmSnapshotCreationTime <serverName> <userName> <password> 
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

# var for display number of Virtual Disks on console
page_size = 40

snapshots = {}

##### ************** End of Configuration Section ************** ########

# Class to hold snapshot information.
class Snapshot:
    def __init__(self, uuid, vm_uuid, create_time):
        self.uuid = uuid
        self.vm_uuid = vm_uuid
        self.raw_create_time = create_time

    def get_uuid(self):
        return self.uuid

    def get_vm_uuid(self):
        return self.vm_uuid

    def get_raw_create_time(self):
        return self.raw_create_time

    def get_formated_create_time(self):
        # http://stackoverflow.com/questions/16995241/datetime-date-fromtimestamp-ignores-hour-and-minute
        return datetime.fromtimestamp(int(self.raw_create_time) // 1e3).strftime('%Y-%m-%d %H:%M:%S')

    def set_uuid_time(self, uuid, create_time):
        self.uuid = uuid
        self.raw_create_time = create_time

# Print functions
def print_debug(out):
    debug_prefix = "[DEBUG] : "
    print (debug_prefix + out)


def print_info(out):
    info_prefix  = "[INFO] : "
    print (info_prefix + out)


def print_error(out):
    error_prefix = "[ERROR] : "
    print(error_prefix + out)


# main
if len(sys.argv) < 4:
    print_error("Insufficient parameters passed for VM latest snapshots")
    print_info("COMMAND USAGE : " + sys.argv[0] +
               " serverName userName password")
    sys.exit(-5)

heading = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- Get Snapshot Creation Time Stamps VMstore ------- "

serverName = sys.argv[1]
userName = sys.argv[2]
password = sys.argv[3]

if debug_mode:
    print()
    print("Arguments fetched from commandline")
    print_debug("ServerName fetched : "+ serverName)
    print_debug("UserName fetched : " +userName)
    print_debug("Password fetched : ********")
    print()

# Login to VMstore

# Payload, header and URL for login call
header = {'content-type': 'application/json'}
payload = {"newPassword": None,
           "username": userName,
           "roles": None,
           "password": password,
           "typeId": "com.tintri.api.rest.vcommon.dto.rbac.RestApiCredentials" }
urlLogin = 'https://'+ serverName +'/api/v310/session/login'

print()
print(heading)
print()
print(sub_heading)
print()
print("Server Name: " + serverName)
print()
print("STEP 1: Login to VMstore")

# Debug Logs to console
if debug_mode:
    print_debug("Going to make the Login call to server : " + serverName)
    print_debug("The URL being used for login is : " + urlLogin)

try:
    # Invoke the login API.
    r = requests.post(urlLogin, json.dumps(payload),
                      headers=header, verify=False)
except requests.ConnectionError:
    print_error("API Connection error occurred")
    sys.exit(-1)
except requests.HTTPError:
    print_error("HTTP error occurred")
    sys.exit(-2)
except requests.Timeout:
    print_error("Request timed out")
    sys.exit(-3)
except Exception:
    print_error("An unexpected error occurred")
    sys.exit(-4)

if debug_mode:
    print_debug("The HTTP Status code for login call to the server " +
                serverName + " is: " + str(r.status_code))

# if HTTP Response is not 200 then raise an exception
if r.status_code is not 200:
    print_error("The HTTP response for login call to the server " +
                serverName + " is not 200")
    sys.exit(-6)

# Debug Logs to console
if debug_mode:
    print_debug("The JSON response of login call to the server " +
                serverName + " is: " + r.text)

# Fetch SessionId from cookie and create header.
session_id = r.cookies['JSESSIONID']
header = {'content-type': 'application/json',
          'cookie': 'JSESSIONID='+session_id }

# Fetch the Snapshots and organize them by VM
print()
print("STEP 2: Fetch Snapshots from VMStore")

# URL for get snapshot invoke
urlGetSnapshot = 'https://' + serverName + '/api/v310/snapshot'
query = {'offset': '0', 'limit': '100'}

# Invoke the Get Snapshot API
r = requests.get(urlGetSnapshot, headers=header, verify=False)
if debug_mode:
    print_debug("The HTTP Status code for getVms call to the server " +
                serverName + " is: " + str(r.status_code))

# if HTTP Response is not 200 then raise an exception
if r.status_code is not 200:
    print_error("The HTTP response for getSnapshot call to the server " +
                serverName + " is not 200")
    sys.exit(-6)

if debug_mode:
    print_debug("The JSON response of getSnapshot call to the server " +
                serverName+" is: " + r.text)

# Loads the paginated result for Snapshots
sss_paginated_result = json.loads(r.text)
total_snapshots = sss_paginated_result['absoluteTotal']
print_info("Total number of snapshots: " + str(total_snapshots))

if total_snapshots == 0:
    sys.exit(0)

# Get the snapshots and check for the latest creation time stamp
items = sss_paginated_result['items']
for snap in items:
    vm_uuid = snap['vmUuid']['uuid']
    uuid = snap['uuid']['uuid']
    create_time = snap['createTime']

    # If VM UUID already exists, check for the latest creation time, or
    # create a new snapshot object.
    if vm_uuid in snapshots.keys():
        a_snap = snapshots[vm_uuid]
        if create_time > snapshots[vm_uuid].get_raw_create_time():
            snapshots[vm_uuid].set_uuid_time(uuid, create_time)
    else:
        a_snap = Snapshot(snap['uuid']['uuid'], vm_uuid, snap['createTime'])
        snapshots[vm_uuid] = a_snap

if debug_mode:
    print_debug("Number of itmes = " + str(len(snapshots)))
    for vm_uuid in snapshots:
        print_debug(vm_uuid + " : " + snapshots[vm_uuid].get_formated_create_time())

# Fetch Virtual Disks from VMStore
print()
print("STEP 3: Fetch VMs from VMStore")

#Header and URL for get virtual machine invoke
urlGetVm = 'https://' + serverName + '/api/v310/vm'
query = {'offset': '0', 'limit': str(page_size)}
first_urlGetVm = urlGetVm + "?" + "offset=0&limit=" + str(page_size)

# Invoke the Get VMs APIs
r = requests.get(first_urlGetVm, headers=header, verify=False)

if debug_mode:
    print_debug("The HTTP Status code for getVms call to the server " +
                serverName + " is: " + str(r.status_code))

# if HTTP Response is not 200 then raise an exception
if r.status_code is not 200:
    print_error("The HTTP response for getVMs call to the server " +
                serverName + " is not 200")
    sys.exit(-6)

if debug_mode:
    print_debug("The JSON response of getVms call to the server " +
                serverName+" is: " + r.text)

# Loads the paginated result for Virtual Machines
vms_paginated_result = json.loads(r.text)

# get the filteredtotal number of Virtual Machines
number_of_vms = int(vms_paginated_result['filteredTotal'])
print()
print_info("Number of Virtual Machines fetched from getVms call to the server " +
            serverName + " is : " + str(number_of_vms))
if number_of_vms == 0:
    print_info("No VMs, so no point in proceeding.")
    sys.exit(0)

table_header = ['No', 'VM', 'Type', 'Last Created Snapshot Time']
table = PrettyTable(table_header)

items = vms_paginated_result["items"]
count = 0
for vm in items:
    vm_uuid = vm['uuid']['uuid']
    vm_name = vm['vmware']['name']
    vm_type = vm['vmware']['hypervisorType']

    # if VM exists in Snapshots, get the create time and add it to the table.
    if vm_uuid in snapshots:
        create_time = snapshots[vm_uuid].get_formated_create_time()

        row = [str(count+1), vm_name, vm_type, create_time]
        table.add_row(row)
        count = count + 1

print(table)

# While 'next' appears, keep getting more.
while 'next' in vms_paginated_result:
    input_char = raw_input("Continue? (y/n): ")
    if input_char != 'y':
        break

    start_count = count

    next_urlGetVm = urlGetVm + "?" + vms_paginated_result["next"]
    if debug_mode:
        print_debug("Next GET Vm URL: " + next_urlGetVm + " (" + str(count) + ")")

    # Get the next page of virtual machines.
    r = requests.get(next_urlGetVm, headers=header, verify=False)
    if debug_mode:
        print_debug("The HTTP Status code for next getVms call to the server " +
                    serverName + " is: " + str(r.status_code))

    # if HTTP Response is not 200 then quit
    if r.status_code is not 200:
        print_error("The HTTP response for next getVMs call to the server " +
                    serverName + " is not 200")
        sys.exit(-6)

    if debug_mode:
        print_debug("The JSON response of next getVms call to the server " +
                    serverName+" is: " + r.text)

    # Loads the paginated result for Virtual Machines
    vms_paginated_result = json.loads(r.text)

    # Create the next table to show.
    table = PrettyTable(table_header)

    items = vms_paginated_result["items"]
    for vm in items:
        vm_uuid = vm['uuid']['uuid']
        vm_name = vm['vmware']['name']
        vm_type = vm['vmware']['hypervisorType']

        # if VM exists in Snapshots, get the create time and add it to the table.
        if vm_uuid in snapshots:
            create_time = snapshots[vm_uuid].get_formated_create_time()

            row = [str(count+1), vm_name, vm_type, create_time]
            table.add_row(row)
            count = count + 1

    if count > start_count:
        print(table)

#Header and URL for logout call
url_VMStore_logout = 'https://' + serverName + '/api/v310/session/logout'

if debug_mode:
    print_debug("The URL being used for logout is : " + url_VMStore_logout)

# Send the logout reauest.
r = requests.get(url_VMStore_logout,headers=header, verify=False)

if debug_mode:
    print_debug("The HTTP Status code for logout call to the server " +
                 serverName + " is: "+str(r.status_code))

# if Http Response is not 204 then raise an exception
if r.status_code is not 204:
    print_error("The HTTP response for logout call to the server " +
                 serverName+" is not 204")
    sys.exit(-6)

print()
print("**********End of Get Snapshot Latest Snapshot Time Script**********")
sys.exit(0)

