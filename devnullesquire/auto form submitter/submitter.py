import random
from datetime import datetime

import pip
import csv

import time

import sys

try:
    import requests
except ImportError:
    pip.main(['install', 'requests'])
    import requests

try:
    import pause
except ImportError:
    pip.main(['install', 'pause'])
    import pause

file_name: str = "data.csv"
if len(sys.argv) > 1:
    file_name = sys.argv[1]

print("INFO: Waiting until 8 AM")
start_time = datetime.now()
start_time.replace(hour=8, minute=0, second=0)
pause.until(start_time)  # wait until 8 AM
print("INFO: Finished waiting, starting POSTs")

with open(file_name) as csvfile:
    rand: random.Random = random.Random()
    reader: csv.DictReader = csv.DictReader(csvfile)
    size: int = sum(1 for _ in reader)
    csvfile.seek(0)
    reader = csv.DictReader(csvfile)
    print("INFO: Amount to send " + str(size))
    count: int = 0
    for row in reader:
        # stop after 7 PM
        if datetime.now().hour >= 19:
            print("WARNING (after hours): Could not post " + row['First Name'] + " " + row['Last Name'] + " from " + row['Company Name'])
            continue

        company: str = row['Company Name']
        first: str = row['First Name']
        last: str = row['Last Name']
        state: str = row['State']
        country: str = row['Country']
        phone: str = row['Phone Number']
        email: str = row['Email']

        details = {
            "elqFormName": "18_JUL_WEBSITE_VIDEO_DemoPageGate",
            "elqSiteId": "1477570687",
            "campaignMemberStatus": "Watched Video",
            "elqCampaignId": "",
            "SFDCid": "",
            "Vendor": "",
            "LeadSource": "",
            "HiddenAssetRequestName": "",
            "HiddenretURL": "",
            "hiddenField": "",
            "ID": "",
            "C_Salutation": "",
            "C_FirstName": first,
            "C_LastName": last,
            "C_EmailAddress": email,
            "C_Company": company,
            "C_BusPhone": phone,
            "C_Country": country,
            "C_State_Prov": state,
            "C_Are_you_looking_to_Purchase_a_Solution1": "",
            "C_ERP_GL_System1": "",
            "C_Annual_Revenue_Range1": "",
            "C_Employees_Range1": "",
            "C_Industry1": "",
            "C_Title": ""
        }

        req: requests.Response = requests.post("http://info.prophix.com/e/f2", details)

        count += 1
        if req.status_code != 200:
            print("ERROR (unsuccessful POST): " + row + " could not be sent")
        else:
        	print("INFO: Send success, progress " + str(count) + "/" + str(size))

        amount: int = 60 * rand.randint(20, 210)
        print("INFO: Sleeping for " + str(amount) + " seconds")
        time.sleep(amount)  # sleep between 20 and 210 (3.5 hours) minutes
