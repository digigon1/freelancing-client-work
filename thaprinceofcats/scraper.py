import pip

def install(package):
	pip.main(['install', package]);

install("beautifulsoup4");
install("python-firebase");
install("requests");

import time
from bs4 import BeautifulSoup
import requests
from html.parser import HTMLParser
from firebase import firebase


class Item(object):
	def __init__(self, siteURL):
		self.siteURL = siteURL;
		self.name = "";
		self.tid = "";
		self.status = "";
		self.lastUpdate = "";
		self.itemURL = "";

baseURL = "http://base/foretag/planerad-noteringar/sok/sida/";
firebase_url = 'https://url'
firebase_secret = '<secret>'
firebase_email = '<email>'

def getDataList():
	dataList = [];
	currentPage = 1;
	while (currentPage < 166):
		print("Current page: " + str(currentPage));
		url = baseURL + str(currentPage);
		r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
		r = r.content
		soup = BeautifulSoup(r, 'html.parser');
		dataTable = soup.find_all("div", { "class" : "box_content"});
		allData = dataTable[1].find_all("td");
		for item in allData:
			itemURL = item.find("a", href=True);
			if (itemURL is not None):
				itemURL = "http://www.nyemissioner.se" + itemURL["href"];
				dataList.append(Item(itemURL));
		currentPage+=1;
	return dataList;

def getItemData(item):
	r = requests.get(item.siteURL, headers={'User-Agent': 'Mozilla/5.0'})
	r = r.content
	soup = BeautifulSoup(r, 'html.parser');
	data = soup.find("div", { "class" : "box_rep"});
	name = data.find("strong").text;
	itemURL = data.find("a", { "class" : "link"});
	itemURL = itemURL["href"];
	dataTable = data.find("table", { "class" : "rows"});
	dataEntries = dataTable.find_all("tr");
	for entry in dataEntries:
		entryData = entry.find_all("td");
		if (entryData[0].text == "Status:"):
			item.status = entryData[1].text;
		if (entryData[0].text == "Tid:"):
			item.tid = entryData[1].text;
	item.itemURL = itemURL;
	item.name = name;
	lastUpdate = data.find("span", class_="small grey");
	lastUpdate = lastUpdate.text.strip();
	lastUpdate = lastUpdate[12:]
	item.lastUpdate = lastUpdate;


db = firebase.FirebaseApplication(firebase_url, None)
auth = firebase.FirebaseAuthentication(firebase_secret, firebase_email)
db.authentication = auth

while (True):
	try:
		testVar = int(input("Enter delay between runs (in seconds): "));
		break;
	except:
		print ("Delay is not an integer");

while(True):
	nameList = [];

	getResult = db.get('/nyemissioner', None)
	if getResult is not None:
		for name in getResult:
			name = str(name);
			name = name.strip("(");
			name = name.strip(")");
			name = name.strip(",");
			name = name.strip("\'");
			nameList.append(name);

	print("Making the list of links...");
	dataList = getDataList();
	for item in dataList:
		print("Getting data for: " + item.siteURL);
		getItemData(item);
		print("Site name: " + item.name);
		print("URL: " + item.itemURL);
		print("Status: " + item.status);
		print("Tid: " + item.tid);
		print("Last update: " + item.lastUpdate);
		print("==========================");
		
	j = 1
	for item in dataList:
		print('Inserting '+item.name+' ('+str(j)+'/'+str(len(dataList))+')')
		j += 1
		for i in range(1, 5):
			try:
				if item.name in nameList:		
					print(db.put('/nyemissioner', item.name.replace('.', '').replace('/', ''), item.__dict__))
				else:
					print(db.patch('/nyemissioner/'+item.name.replace('.', '').replace('/', ''), item.__dict__))
				break
			except Exception as e:
				print('Attempt number '+str(i)+' for '+item.name)
	print ("Next scrape in " + str(testVar) + " seconds");
	time.sleep(testVar);
