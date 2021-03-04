from multiprocessing import Pool

from bs4 import BeautifulSoup
import requests
import json

flatten = lambda l: [item for sublist in l for item in sublist]

def get_links(page):
	global payload
	print(page)
	while True:
		try:
			url = "https://appsmqa.doh.state.fl.us/MQASearchServices/HealthCareProviders/IndexPaged"
			headers = {
			    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
			    'Cache-Control': "no-cache"
			}
			querystring = {"page":str(page)}
			response = session.request("POST", url, data=payload, headers=headers, params=querystring, timeout=None)
			soup = BeautifulSoup(response.text, 'html.parser')
			
			new_links = [tr.find('a')['href'] for tr in soup.find_all('tr')[1:-1]]

			if len(new_links) > 0:
				return new_links
		except Exception as e:
			print(e)

session = requests.Session()

#Pain Management Clinic
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1516\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#osteopathic physician
payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1901\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#chiropractic physician
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n501\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#medical doctor
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1501\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

headers = {
    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    'Cache-Control': "no-cache"
}

response = session.request("POST", "https://appsmqa.doh.state.fl.us/MQASearchServices/HealthCareProviders/", data=payload, headers=headers, timeout=None)

soup = BeautifulSoup(response.text, 'html.parser') 
prev_len = 0
links = [tr.find('a')['href'] for tr in soup.find_all('tr')[1:-1]]

max_total = int(soup.find('caption').text.split('\r\n')[1].split(':')[1])

url = "https://appsmqa.doh.state.fl.us/MQASearchServices/HealthCareProviders/IndexPaged"

page = 2
max_page = (max_total // 20) + 1

pages = range(2, max_page + 1)
with Pool(20) as p:
	links = flatten(p.map(get_links, pages))
	
num = 0
#print(len(links))

def get_line(l):
	global num
	print(num)

	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l.replace('LicenseVerification', 'Details'), timeout=None).text, 'html.parser')
		except Exception as e:
			print(e)

	try:
		name = soup.find('h3').text.replace('  ', ' ').strip()
	except Exception as e:
		return get_line(l)
	#print('Name: ' + name)

	addresses = '; '.join([div.text.replace(',', '').strip() for div in soup.find_all('div', class_='toUpper') if len(div.text.strip()) > 0][1:])
	#print('Address: ' + addresses)

	add_parts = addresses.split(';')
	try:
		zip_code = add_parts[len(add_parts) - 2 if (len(add_parts) - 2) >= 0 else None].split(' ')[-1]
		city = ' '.join(add_parts[len(add_parts) - 2].split(' ')[0:-2]).strip()
	except Exception as e:
		zip_code = ''
		city = ''

	email = soup.find('strong').text.strip()
	if '@' in email:
		pass
		#print('Email: ' + email)
	else:
		email = ''
		#print('Email:')

	states = '; '.join([tr.text.replace('\n', '').replace('\r', '').strip().split('  ')[0] for tr in soup.find('div', class_='active').find_all('tr')][1:])
	#print('Other states: ' + states)

	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l, timeout=None).text, 'html.parser')
		except Exception as e:
			print(e)

	dds = soup.find_all('dd')
	dts = soup.find_all('dt')

	profession = ''
	issue_date = ''
	public_complaint = ''
	qualifications = ''
	for i in range(0, len(dts)):
		tag = dts[i].text.replace('\n', '').replace('\r', '').strip()
		if tag == 'Profession':
			profession = dds[i].text.replace('\n', '').replace('\r', '').strip()
		elif tag == 'License Original Issue Date':
			issue_date = dds[i].text.replace('\n', '').replace('\r', '').strip()
		elif tag == 'Public Complaint':
			public_complaint = dds[i].text.replace('\n', '').replace('\r', '').strip()
		elif tag == '':
			qualifications = dds[i].text.replace('\n', '').replace('\r', '').strip()

	num += 1

	return ','.join([name, profession, addresses, zip_code, city, qualifications, email, states, issue_date, public_complaint])


csv_output = ['Name,Profession,Address,Zip Code,City,Qualifications,Email,Other States,Issue Date,Public Complaint']

with Pool(20) as p:
	csv_output.extend(p.map(get_line, links))

'''
for l in links:
	#print(str(link) + '/' + str(len(links)))
	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l.replace('LicenseVerification', 'Details'), timeout=None).text, 'html.parser')
		except Exception as e:
			#print(e)

	name = soup.find('h3').text.replace('  ', ' ').strip()
	#print('Name: ' + name)

	addresses = '; '.join([div.text.replace(',', '').strip() for div in soup.find_all('div', class_='toUpper') if len(div.text.strip()) > 0][1:])
	#print('Address: ' + addresses)

	add_parts = addresses.split(';')
	try:
		zip_code = add_parts[len(add_parts) - 2].split(' ')[-1]
		city = add_parts[len(add_parts) - 2].split(' ')[0]
	except Exception as e:
		zip_code = ''
		city = ''

	email = soup.find('strong').text.strip()
	if '@' in email:
		#print('Email: ' + email)
	else:
		email = ''
		#print('Email:')

	states = '; '.join([tr.text.replace('\n', '').replace('\r', '').strip().split('  ')[0] for tr in soup.find('div', class_='active').find_all('tr')][1:])
	#print('Other states: ' + states)

	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l, timeout=None).text, 'html.parser')
		except Exception as e:
			#print(e)

	dds = soup.find_all('dd')
	dts = soup.find_all('dt')

	profession = ''
	issue_date = ''
	public_complaint = ''
	qualifications = ''
	for i in range(0, len(dts)):
		tag = dts[i].text.replace('\n', '').replace('\r', '').strip()
		if tag == 'Profession':
			profession = dds[i].text.replace('\n', '').replace('\r', '').strip()
			#print('Profession: ' + profession)
		elif tag == 'License Original Issue Date':
			issue_date = dds[i].text.replace('\n', '').replace('\r', '').strip()
			#print('Issue date: ' + issue_date)
		elif tag == 'Public Complaint':
			public_complaint = dds[i].text.replace('\n', '').replace('\r', '').strip()
			#print('Public complaint: ' + public_complaint)
		elif tag == '':
			qualifications = dds[i].text.replace('\n', '').replace('\r', '').strip()
			#print('Qualifications: ' + qualifications)

	csv_output.append(','.join([name, profession, addresses, zip_code, qualifications, email, states, issue_date, public_complaint]))

	#print()
	link += 1
'''

with open('osteo.csv', 'w') as f:
	for csv in csv_output:
		f.write(csv + '\n')