from bs4 import BeautifulSoup
import requests
import json

session = requests.Session()

#Pain Management Clinic
payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1516\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#osteopathic physician
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Board\"\r\n\r\n5\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n1901\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

#chiropractic physician
#payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Board\"\r\n\r\n5\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.Profession\"\r\n\r\n501\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"SearchDto.LicenseStatus\"\r\n\r\nACT\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

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
headers = {
    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    'Cache-Control': "no-cache"
}

page = 2
while prev_len != len(links):
	print(page)
	querystring = {"page":str(page)}
	response = session.request("GET", url, data=payload, headers=headers, params=querystring, timeout=None)
	soup = BeautifulSoup(response.text, 'html.parser')
	
	new_links = [tr.find('a')['href'] for tr in soup.find_all('tr')[1:-1]]

	prev_len = len(links)

	links.extend(new_links)

	page += 1


csv_output = ['Name,Address,Email,Other States']

link = 1
for l in links:
	print(str(link) + '/' + str(len(links)))
	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l, timeout=None).text, 'html.parser')
		except Exception as e:
			print(e)


	name = soup.find('h3').text.replace('  ', ' ').strip()
	print('Name: ' + name)

	soup = None
	while soup == None:
		try:
			soup = BeautifulSoup(requests.get("https://appsmqa.doh.state.fl.us" + l.replace('LicenseVerification', 'Details'), timeout=None).text, 'html.parser')
		except Exception as e:
			print(e)

	try:
		email = soup.find('strong').text.strip()
		if '@' in email:
			print('Email: ' + email)
		else:
			email = ''
			print('Email:')
	except Exception as e:
		email = ''
		print('Email:')

	addresses = '; '.join([div.text.replace(',', '').strip() for div in soup.find_all('div', class_='toUpper') if len(div.text.strip()) > 0][:])
	print('Address: ' + addresses)

	states = '; '.join([tr.text.replace('\n', '').replace('\r', '').strip().split('  ')[0] for tr in soup.find('div', class_='active').find_all('tr')][:])
	print('Other states: ' + states)

	csv_output.append(','.join([name.replace(',', ''), addresses, email, states.replace(',', '')]))

	print()
	link += 1

with open('pain.csv', 'w') as f:
	for csv in csv_output:
		f.write(csv + '\n')