import feedparser
from bs4 import BeautifulSoup
import MySQLdb

import urllib.parse, urllib.request
import re
import urllib
import json 

import time

ignore_list = [['4', '(Reporting)'], ['4/A', '(Reporting)'], ['3', '(Reporting)'], ['5', '(Reporting)'], 
				['SC 13G', '(Filed by)'], ['SC 13D/A', '(Filed by)'], ['SC 13G/A', '(Filed by)'],
				['425', '(Filed by)'], ['SC 13G/A', '(Filed by)']]

def get_stock_price(name):
	if name == '':
		return ''

	for x in range(0, 5):
		with urllib.request.urlopen('https://finance.yahoo.com/quote/' + name + '?p=' + name) as quote:
			soup = BeautifulSoup(quote.read().decode(), 'html.parser')
			try:
				return soup.find_all(id='quote-header-info')[0].find_all('span')[1].text  # ugly, check if works
			except Exception as e:
				print('Stock price for ' + name + ' not found')
				return ''
	return ''


db = MySQLdb.connect('host', 'user', r'password', 'database')

while True:
	d = feedparser.parse('https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&owner=include&start=0&count=100&output=atom')
	curr_time = time.time()
	for e in reversed(d.entries):
		# print(e.title.split(' - ')[1].split('(')[0])
		# print(e)

		found = False
		for ignore in ignore_list:
			if e.title.startswith(ignore[0] + ' -') and ignore[1] in e.title:
				found = True
				break

		if found:
			continue

		cursor = db.cursor()
		cursor.execute("""SELECT * from news where link = %s""", (e.link, ))
		if cursor.rowcount < 1:
			while True:
				try:
					with urllib.request.urlopen(e.link) as edgar:
						soup = BeautifulSoup(edgar.read().decode(), 'html.parser')

						form_title = soup.find(id='formName').text.split(':')[0]

						for company in reversed(soup.find_all('div', class_='companyInfo')):

							links = company.find_all(class_='identInfo')[0].find_all('a')
							search_term = ''
							if links:
								file_no = links[0].text
								
								if len(file_no.split('-')) > 2:
									with urllib.request.urlopen('https://www.sec.gov/cgi-bin/browse-edgar?filenum=' + urllib.parse.quote('-'.join(file_no.split('-')[:2])) + '&action=getcompany') as parent:
										edgar_parent = BeautifulSoup(parent, 'html.parser')
										# print(edgar_parent)
										s = edgar_parent.find_all('span', class_='companyName')[0]
										search_term = s.text.split(' CIK#')[0]
								
							if search_term == '':
								s = company.find_all('span', class_='companyName')[0]
								search_term = s.text.split('(', 1)[0]
					

							search_term = search_term.strip().replace('.', '').replace(',', '')
							search_term = re.sub(' inc$', '', search_term, flags=re.I)

							name = ''
					
							eoddata = 'http://www.eoddata.com/Search.aspx?s=' + urllib.parse.quote(search_term)
							print(eoddata)
							with urllib.request.urlopen(eoddata) as eod:
								eod_soup = BeautifulSoup(eod.read().decode(), 'html.parser')
								print('For ' + search_term + ' found:')
								links = eod_soup.find_all('table', class_='quotes')[0].find_all('a')
								if len(links) > 0:
									name = links[0].text

							if name == '':
								yahoo = 'http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=' + urllib.parse.quote(search_term) + '&lang='
								# print(yahoo)
								with urllib.request.urlopen(yahoo) as url:
									data = json.loads(url.read().decode())
									result = data['ResultSet']['Result']
									if result:
										name = result[0]['symbol']

							if name == '' or '.' in name or '^' in name:
								bloomberg = 'https://www.bloomberg.com/markets/symbolsearch?query=' + urllib.parse.quote(search_term) + '&commit=Find+Symbols'
								print(bloomberg)
								with urllib.request.urlopen(bloomberg) as bloom:
									bloom_soup = BeautifulSoup(bloom.read().decode(), 'html.parser')
									print('For ' + search_term + ' found:')
									name = bloom_soup.find_all('td', class_='symbol')[0].text.split(':')[0]


							if name != '':
								price = get_stock_price(name)
								link = 'http://www.sec.gov'
								link += soup.find_all('table')[0].find_all('a')[0]['href']
								print(link)  # Deal with duplicates and keep these links
								print(e.updated + ', ' + e.title + ', ' + name + ' (' + price + '), ' + e.link)
								cursor = db.cursor()
								try:
									cursor.execute("""INSERT INTO news (updated, title, ticker, price, link, form_title, origin) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (e.updated , e.title, name, price, link, form_title, 'EDGAR'))
									db.commit()
								except:
									db.rollback()
								print()
								break
					break
				except Exception as exc:
					print(exc)
					print('retrying ' + e.link)

	try:
		time.sleep(curr_time - time.time() + 1)
		print('paused')
	except Exception as e:
		pass

