import feedparser
from bs4 import BeautifulSoup
import MySQLdb

import traceback

#import urllib.parse, urllib.request
import re
import urlparse
import urllib

import urllib2
import sys

import json 

import time

ignore_list = [['4', '(Reporting)'], ['4/A', '(Reporting)'], ['3', '(Reporting)'], ['5', '(Reporting)'], 
				['SC 13G', '(Filed by)'], ['SC 13D/A', '(Filed by)'], ['SC 13G/A', '(Filed by)'],
				['425', '(Filed by)'], ['SC 13G/A', '(Filed by)']]

last10k_api_key = '<apiKey>'

def get_stock_data(name):
	if name == '':
		return ('', '')

	req = urllib2.Request('https://api.iextrading.com/1.0/stock/' + name + '/quote')
	try:
		resp = urllib2.urlopen(req)
		j = json.loads(resp.read())
		print(j)
		return (j['latestPrice'], j['changePercent'])
	except Exception as e:
		return ('', '')

	#for x in range(0, 5):
	#	quote = urllib.urlopen('https://finance.yahoo.com/quote/' + name + '?p=' + name)
	#	soup = BeautifulSoup(quote.read().decode('utf-8'), 'html.parser')
	#	try:
	#		return soup.find_all(id='quote-header-info')[0].find_all('span')[1].text  # ugly, check if works
	#	except Exception as e:
	#		print('Stock price for ' + name + ' not found')
	#		return ''
	#return ''

def search_database(CIK):
	cursor.execute("""SELECT ticker from cik where cik = %s""", (CIK, ))
	if cursor.rowcount > 0:
		row = cursor.fetchone()
		print(row)
		return row[0]
	else:
		return ''

def search_last10k(CIK):
	print(CIK)
	req = urllib2.Request('https://services.last10k.com/v1/company/' + CIK + '/ticker')
	req.add_header('Ocp-Apim-Subscription-Key', last10k_api_key)
	try:
		resp = urllib2.urlopen(req)
		return json.loads(resp.read()).upper()
	except Exception as e:
		return ''


#def search_rank_and_filed(search_term):
#	yahoo = 'http://rankandfiled.com/data/search?q=' + urllib.pathname2url(search_term.lower())
#	url = urllib.urlopen(yahoo)
#	data = json.loads(url.read().decode('utf-8'))
#	result = data['results']
#	try:
#		if result:
#			print(result)
#			print(result[0].split('[')[1].split(']')[0])
#			return result[0].split('[')[1].split(']')[0]
#		return ''
#	except Exception as e:
#		return ''

def search_eod(search_term):
	eoddata = 'http://www.eoddata.com/Search.aspx?s=' + urllib.pathname2url(search_term)
	eod = urllib.urlopen(eoddata)
	eod_soup = BeautifulSoup(eod, 'html.parser')
	links = eod_soup.find_all('table', class_='quotes')[0].find_all('a')
	if len(links) > 0:
		return links[0].text.strip()
	return ''

def search_yahoo(search_term):
	yahoo = 'http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=' + urllib.pathname2url(search_term) + '&lang='
	url = urllib.urlopen(yahoo)
	data = json.loads(url.read().decode('utf-8'))
	result = data['ResultSet']['Result']
	if result:
		return result[0]['symbol'].strip()
	return ''

def search_bloomberg(search_term):
	bloomberg = 'https://www.bloomberg.com/markets/symbolsearch?query=' + urllib.pathname2url(search_term) + '&commit=Find+Symbols'
	bloom = urllib.urlopen(bloomberg)
	bloom_soup = BeautifulSoup(bloom, 'html.parser')
	symbols = bloom_soup.find_all('td', class_='symbol')
	if len(symbols) > 0:
		return symbols[0].text.split(':')[0].strip()
	return ''

def search_all(search_term, functions):
	name = ''

	for fun in functions:
		name = fun(search_term)
		if name != '' and check.match(name) is not None:
			break

	return name

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

		cik = e.title.split('(')[1].split(')')[0]

		while True:
			try:
				edgar = urllib.urlopen(e.link)
				soup = BeautifulSoup(edgar.read().decode('utf-8'), 'html.parser')

				link = 'http://www.sec.gov'
				link += soup.find_all('table')[0].find_all('a')[0]['href']

				cursor = db.cursor()
				cursor.execute("""SELECT * from news where link = %s""", (link, ))
				if cursor.rowcount < 1:

					form_title = soup.find(id='formName').text.split(':')[0]

					name = search_database(cik)

					if name == '':
						name = search_last10k(cik)

					if name == '':
						search_term = e.title.split(' - ')[1].split('(')[0]

						print('searching ' + search_term)

						search_term = search_term.strip().replace('.', '').replace(',', '')
						search_term = re.sub('(?i) inc$', '', search_term)
					
						check = re.compile('[^a-zA-Z]')
						
						name = search_all(search_term, [search_eod, search_yahoo, search_bloomberg])

						#name = search_eod(search_term)
						#if name == '' or check.match(name) is None:
						#	name = search_yahoo(search_term)
						#if name == '' or check.match(name) is None:
						#	name = search_bloomberg(search_term)

						if name != '' and check.match(name) is None:
							cursor.execute("""INSERT INTO cik (cik, ticker) VALUES (%s, %s)""", (cik, name))
					
					stock_data = get_stock_data(name)
					price = ''
					perc_change = ''
					try:
						price = stock_data[0]
						if price != '':
							price = '%.2f' % price

						perc_change = stock_data[1]
						if perc_change != '':
							perc_change = '%.2f' % (perc_change * 100)
					except Exception as e:
						traceback.print_exc()
						sys.stderr.write(e)
						sys.stderr.write(cik)
						sys.stderr.write(name)

					try:
						if price != '':
							print('company found, price: ' + price)
						else:
							print('inserting empty ticker')
						cursor = db.cursor()
						cursor.execute("""INSERT INTO news (updated, title, ticker, price, link, form_title, origin, perc_change) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (e.updated , e.title, name, price, link, form_title, 'EDGAR', perc_change))
						db.commit()
						break
					except Exception as ex:
						print(ex)
						db.rollback()
				break

			except Exception as exc:
				traceback.print_exc()
				print('retrying ' + e.link)

	try:
		time.sleep(curr_time - time.time() + 1)
		print('paused')
	except Exception as e:
		pass

