from bs4 import BeautifulSoup
import requests
import re
import threading
from operator import itemgetter
import os
import csv

max_threads = 50

html = requests.get('https://www.archdaily.com/search/projects')
soup = BeautifulSoup(html.text, 'html.parser')
latest = soup.find_all('a', class_='afd-search-list__link')[0].get('href')
max_page = int(re.search(r'\d+', latest).group())
min_page = -1

output_file = 'file.csv'
results = []
if os.path.isfile(output_file):
	with open(output_file, 'r') as csv_file:
		reader = csv.reader(csv_file)
		next(reader)
		for row in reader:
			if min_page == -1:
				min_page = int(row[0])

			results.append([int(row[0]), row[1], row[2], row[3], row[4], row[5]])
else:
	min_page = 2

def test_page(page):
	global results
	try:
		link = 'https://www.archdaily.com/'+str(page)
		requests.head(link).raise_for_status()
		html = requests.get(link)
		soup = BeautifulSoup(html.text, 'html.parser')

		try:
			if soup.find_all('li', class_='afd-breadcrumbs__item')[1].find('span').string.strip().startswith('Artic'):
				return
		except Exception as e:
			print('\n\n')
			print('------------------------------------')
			print(page)
			print('------------------------------------')
			print('\n\n')
			return

		title = soup.find_all('title')[0].string.rsplit('|',1)[0].strip().replace(',', '').split(' / ', 1)
		if len(title) < 2:
			title.append('')
		t = [page, title[0], title[1]]
		m = soup.find(id='single-map')
		if m is not None:
			map_link = m.find_all('a')[0]
			t = t+[map_link.get('data-latitude'), map_link.get('data-longitude'), link]
		else:
			t = t+['', '', link]
		print(t)
		results.append(t)
	except requests.exceptions.HTTPError as e:
		print(str(page)+' not found')


threads = []
try:
	for page in range(min_page + 1, max_page + 1):
		while threading.active_count() > max_threads:
			continue

		t = threading.Thread(target=test_page, args=(page, ))
		threads.append(t)
		t.start()
except KeyboardInterrupt as e:
	print('Interrupted, saving progress so far')
	pass
else:
	print('Saving file')

for t in threads:
	try:
		t.join()
	except Exception as e:
		pass

with open(output_file, 'wb') as f:
	results.sort(key=itemgetter(0), reverse=True)
	f.write(b'Page,Title,Architect,Latitude,Longitude,Source\n')
	for r in results:
		f.write((','.join([str(s) for s in r]) + '\n').encode('utf-8', 'replace'))
