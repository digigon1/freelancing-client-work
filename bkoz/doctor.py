from bs4 import BeautifulSoup
import requests
import json

session = requests.Session()

#Pain Management Clinic
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1516\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#osteopathic physician
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1901\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#chiropractic physician
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n501\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#medical doctor
payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1501\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

headers = {
    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    'Cache-Control': "no-cache"
}

response = session.request("POST", "https://appsmqa.doh.state.fl.us/MQASearchServices/HealthCareProviders/", data=payload, headers=headers, timeout=None)

soup = BeautifulSoup(response.text, 'html.parser') 
prev_len = 0
links = [tr.find('a')['href'] for tr in soup.find_all('tr')[1:-1]]

url = "https://appsmqa.doh.state.fl.us/MQASearchServices/HealthCareProviders/IndexPaged"
payload = ""

page = 2
att = 0
while att < 5:
	print(page)
	querystring = {"page":str(page)}
	response = session.request("GET", url, data=payload, headers=headers, params=querystring, timeout=None)
	soup = BeautifulSoup(response.text, 'html.parser')
	
	new_links = [tr.find('a')['href'] for tr in soup.find_all('tr')[1:-1]]

	prev_len = len(links)

	links.extend(new_links)

	if prev_len == len(links):
		att += 1
	else:
		att = 0
		page += 1
		for x in range(1, 50000000):
			pass
	break

print(len(links))


csv_output = ['Name,Profession,Address,Zip Code,Qualifications,Email,Other States,Issue Date,Public Complaint']

link = 1
for l in links:
	print(str(link) + '/' + str(len(links)))
	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l.replace('LicenseVerification', 'Details'), timeout=None).text, 'html.parser')
		except Exception as e:
			print(e)

	name = soup.find('h3').text.replace('  ', ' ').strip()
	print('Name: ' + name)

	addresses = '; '.join([div.text.replace(',', '').strip() for div in soup.find_all('div', class_='toUpper') if len(div.text.strip()) > 0][1:])
	print('Address: ' + addresses)

	add_parts = addresses.split(';')
	try:
		zip_code = add_parts[len(add_parts) - 2].split(' ')[-1]
		county = add_parts[len(add_parts) - 2].split(' ')[0]
	except Exception as e:
		zip_code = ''
		county = ''

	email = soup.find('strong').text.strip()
	if '@' in email:
		print('Email: ' + email)
	else:
		email = ''
		print('Email:')

	states = '; '.join([tr.text.replace('\n', '').replace('\r', '').strip().split('  ')[0] for tr in soup.find('div', class_='active').find_all('tr')][1:])
	print('Other states: ' + states)

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
			print('Profession: ' + profession)
		elif tag == 'License Original Issue Date':
			issue_date = dds[i].text.replace('\n', '').replace('\r', '').strip()
			print('Issue date: ' + issue_date)
		elif tag == 'Public Complaint':
			public_complaint = dds[i].text.replace('\n', '').replace('\r', '').strip()
			print('Public complaint: ' + public_complaint)
		elif tag == '':
			qualifications = dds[i].text.replace('\n', '').replace('\r', '').strip()
			print('Qualifications: ' + qualifications)

	csv_output.append(','.join([name, profession, addresses, zip_code, qualifications, email, states, issue_date, public_complaint]))

	print()
	link += 1

with open('doctor.csv', 'w') as f:
	for csv in csv_output:
		f.write(csv + '\n')