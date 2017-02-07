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
from prettytable import PrettyTable

"""
 This Python script is responsible for getting the list of alerts and showing it on console.
 A user can make changes in the configuration section to change the configurations like debug_mode, number of items to be displayed on console
 if debug_mode is set to False; then JSON response won't be printed on console
 Command usage: GetAlertClient <serverName> <userName> <password>
"""

##### ************** Configurations to be done by end user ************** ########

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False
number_of_items_to_display_on_console = 5

##### ************** End of Configuration Section ************** ########


debug_prefix = "[DEBUG] : "
info_prefix = "[INFO] : "
error_prefix = "[ERROR] : "

if len(sys.argv) < 4:
    print(error_prefix+"Insufficient parameters passed for getting Alerts")
    print(info_prefix+"COMMAND USAGE : GetAlertClient serverName userName password")
    sys.exit(-5)

header = "********************************* Tintri Inc. *********************************"
sub_heading = " ------- GetAlerts ------- "

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


# Fetch Inbox Alerts from VMStore
print()
print("STEP 2: Fetch Inbox Alerts and Notices from VMStore")


#Header and URL for Inbox Alerts and Notices call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetInboxAlertsAndNotices = 'https://'+serverName+'/api/v310/alert'

# Debug Logs to console
if debug_mode:
    print(debug_prefix+"Going to make the getAlertsAndNotices(inbox) call to server : "+serverName)
    print(debug_prefix+"The URL being used for getAlertsAndNotices(inbox) is : "+urlGetInboxAlertsAndNotices)

# Trying to fetch inbox alerts and notices from the vmstore (GET request)
r = requests.get(urlGetInboxAlertsAndNotices,headers=headers, verify=False)


if debug_mode:
    print(debug_prefix+"The HTTP Status code for getAlertsAndNotices(inbox) call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print(error_prefix+"The HTTP response for getAlertsAndNotices(inbox) call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("The Json response of getAlertsAndNotices(inbox) call to the server "+serverName+" is: "+r.text)

alerts_notices_paginated_result = json.loads(r.text)
number_of_inbox_alerts_notices = int(alerts_notices_paginated_result["filteredTotal"])
print("\t"+info_prefix+"Number of Inbox-ed Alerts fetched from getAlertsAndNotices(inbox) call to the server "+serverName+" is : "+str(number_of_inbox_alerts_notices))

# Fetch Inbox Alerts from VMStore
print()
print("STEP 3: Fetch Inbox Alerts from VMStore")


#Header and URL for Inbox Alerts call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetInboxAlerts = 'https://'+serverName+'/api/v310/alert?severity=alert'

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the getAlerts(inbox) call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for getAlerts(inbox) is : "+urlGetInboxAlerts)

# Trying to fetch inbox alerts from the vmstore (GET request)
r = requests.get(urlGetInboxAlerts,headers=headers, verify=False)


if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getAlerts(inbox) call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getAlerts(inbox) call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getAlerts(inbox) call to the server "+serverName+" is: "+r.text)

inbox_alerts_paginated_result = json.loads(r.text)
number_of_inbox_alerts = int(inbox_alerts_paginated_result["filteredTotal"])
print("\t"+info_prefix+"Number of Inbox-ed Alerts fetched from getAlerts(inbox) call to the server "+serverName+" is : "+str(number_of_inbox_alerts))

tableHeader =  ['No.', 'Inbox Alert Message']
x = PrettyTable(tableHeader)
if number_of_inbox_alerts > number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First "+str(number_of_items_to_display_on_console)+" Inbox-ed Alert messages fetched : ")
    items = inbox_alerts_paginated_result["items"]
    for count in range(0,number_of_items_to_display_on_console):
        row = [str(count+1),items[count]["message"]]
        x.add_row(row)
    print(x)
elif number_of_inbox_alerts_notices > 0 and number_of_inbox_alerts_notices < number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First Inbox-ed Alert message fetched : ")
    items = inbox_alerts_paginated_result["items"]
    row = (str(1),items[0]["message"])
    x.add_row(row)
    print(x)
elif number_of_inbox_alerts_notices == 0:
    print("\t"+info_prefix+"No Inbox-ed Alerts present")



# Fetch Inbox Notices from VMStore
print()
print("STEP 4: Fetch Inbox Notices from VMStore")


#Header and URL for Inbox Alerts call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetInboxNotices = 'https://'+serverName+'/api/v310/alert?severity=notice'

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the getNotices(inbox) call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for getNotices(inbox) is : "+urlGetInboxNotices)

# Trying to fetch inbox notices from the vmstore (GET request)
r = requests.get(urlGetInboxNotices,headers=headers, verify=False)


if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getNotices(inbox) call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getNotices(inbox) call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getNotices(inbox) call to the server "+serverName+" is: "+r.text)

notices_paginated_result = json.loads(r.text)
number_of_inbox_notices = int(notices_paginated_result["filteredTotal"])
print("\t"+info_prefix+"Number of Inbox-ed Notices fetched from getNotices(inbox) call to the server "+serverName+" is : "+str(number_of_inbox_notices))

tableHeader =  ['No.', 'Inbox Notice Message']
x = PrettyTable(tableHeader)

if number_of_inbox_notices > number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First "+str(number_of_items_to_display_on_console)+" Inbox-ed Notice messages fetched : ")
    items = notices_paginated_result["items"]
    for count in range(0,number_of_items_to_display_on_console):
        row = [str(count+1),items[count]["message"]]
        x.add_row(row)
    print(x)
elif number_of_inbox_alerts_notices > 0 and number_of_inbox_alerts_notices < number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First Inbox-ed Notice message fetched : ")
    items = notices_paginated_result["items"]
    row = [str(1),items[0]["message"]]
    x.add_row(row)
    print(x)
elif number_of_inbox_alerts_notices == 0:
    print("\t"+info_prefix+"No Inbox-ed Notices present")

# Fetch Archived Alerts and Notices from VMStore
print()
print("STEP 5: Fetch Archived Alerts and Notices from VMStore")


#Header and URL for Archived Alerts and Notices call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetArchivedAlertsAndNotices = 'https://'+serverName+'/api/v310/alert?state=archived'

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the getAlertsAndNotices(archived) call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for getAlertsAndNotices(archived) is : "+urlGetArchivedAlertsAndNotices)

# Trying to fetch archived alerts and  notices from the vmstore (GET request)
r = requests.get(urlGetArchivedAlertsAndNotices,headers=headers, verify=False)


if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getAlertsAndNotices(archived) call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getAlertsAndNotices(archived) call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getAlertsAndNotices(archived) call to the server "+serverName+" is: "+r.text)

alerts_notices_paginated_result_archived = json.loads(r.text)
number_of_archived_alerts_notices = int(alerts_notices_paginated_result_archived["filteredTotal"])
print("\t"+info_prefix+"Number of archived Alerts and Notices fetched from getAlertsAndNotices(archived) call to the server "+serverName+" is : "+str(number_of_archived_alerts_notices))


# Fetch Archived Alerts from VMStore
print()
print("STEP 6: Fetch Archived Alerts from VMStore")


#Header and URL for Archived Alerts and Notices call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetArchivedAlerts = 'https://'+serverName+'/api/v310/alert?state=archived&severity=alert'

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the getAlerts(archived) call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for getAlerts(archived) is : "+urlGetArchivedAlerts)

# Trying to fetch archived alerts from the vmstore (GET request)
r = requests.get(urlGetArchivedAlerts,headers=headers, verify=False)


if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getAlerts(archived) call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getAlerts(archived) call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getAlerts(archived) call to the server "+serverName+" is: "+r.text)

alerts_paginated_result_archived = json.loads(r.text)
number_of_archived_alerts = int(alerts_paginated_result_archived["filteredTotal"])
print("\t"+info_prefix+"Number of archived Alerts fetched from getAlerts(archived) call to the server "+serverName+" is : "+str(number_of_archived_alerts))


tableHeader =  ['No.', 'Archived Alert Message']
x = PrettyTable(tableHeader)

if number_of_archived_alerts > number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First "+str(number_of_items_to_display_on_console)+" Archived Alert messages fetched : ")
    items = alerts_paginated_result_archived["items"]
    for count in range(0,number_of_items_to_display_on_console):
        row = [str(count+1),items[count]["message"]]
        x.add_row(row)
    print(x)
elif number_of_archived_alerts > 0 and number_of_archived_alerts < number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First Archived Alert message fetched : ")
    items = alerts_paginated_result_archived["items"]
    row = [str(1),items[0]["message"]]
    x.add_row(row)
    print(x)
elif number_of_inbox_alerts_notices == 0:
    print("\t"+info_prefix+"No Archived Alerts present")


# Fetch Archived Alerts from VMStore
print()
print("STEP 7: Fetch Archived Notices from VMStore")


#Header and URL for Archived Alerts and Notices call
headers = {'content-type': 'application/json','cookie': 'JSESSIONID='+session_id}
urlGetArchivedNotices = 'https://'+serverName+'/api/v310/alert?state=archived&severity=notice'

# Debug Logs to console
if debug_mode:
    print("\t"+debug_prefix+"Going to make the getNotices(archived) call to server : "+serverName)
    print("\t"+debug_prefix+"The URL being used for getNotices(archived) is : "+urlGetArchivedNotices)

# Trying to fetch archived notices from the vmstore (GET request)
r = requests.get(urlGetArchivedNotices,headers=headers, verify=False)


if debug_mode:
    print("\t"+debug_prefix+"The HTTP Status code for getNotices(archived) call to the server "+serverName + " is: "+str(r.status_code))

# if Http Response is not 200 then raise an exception
if r.status_code is not 200:
    print("\t"+error_prefix+"The HTTP response for getNotices(archived) call to the server "+serverName+" is not 200")
    sys.exit(-6)


if debug_mode:
    print("\t"+debug_prefix+"The Json response of getNotices(archived) call to the server "+serverName+" is: "+r.text)

notices_paginated_result_archived = json.loads(r.text)
number_of_archived_notices = int(notices_paginated_result_archived["filteredTotal"])
print("\t"+info_prefix+"Number of archived notices fetched from getNotices(archived) call to the server "+serverName+" is : "+str(number_of_archived_notices))


tableHeader =  ['No.', 'Archived Notice Message']
x = PrettyTable(tableHeader)

if number_of_archived_notices > number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First "+str(number_of_items_to_display_on_console)+" Archived Notice messages fetched : ")
    items = notices_paginated_result_archived["items"]
    for count in range(0,number_of_items_to_display_on_console):
        row = [str(count+1),items[count]["message"]]
        x.add_row(row)
    print(x)
elif number_of_archived_notices > 0 and number_of_archived_notices < number_of_items_to_display_on_console:
    print("\t"+info_prefix+"First Archived Notice message fetched : ")
    items = notices_paginated_result_archived["items"]
    row = [str(1),items[0]["message"]]
    x.add_row(row)
    print(x)
elif number_of_inbox_alerts_notices == 0:
    print("\t"+info_prefix+"No Archived Notices present")

# Logout of VMStore

print()
print("STEP 7: Logout from VMStore")

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
print("**********End of GetAlerts Sample Client Script**********")

