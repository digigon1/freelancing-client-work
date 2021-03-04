from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import re
import webbrowser
import sys

if len(sys.argv) < 2:
	print("usage: py serato.py <playlist>")
	sys.exit()

OPEN_BROWSER = True

url = sys.argv[1]

fp = urllib.request.urlopen(url)
mybytes = fp.read()
mystr = mybytes.decode("utf8")
fp.close()

soup = BeautifulSoup(mystr, "lxml")

titles = []
if url.find("serato.com") != -1:
	divs = soup.find_all('div', id=re.compile("^track_\d+"))

	for d in divs:
		title = d.select('div')[1].get_text(strip=True)
		if not re.match("^\d+:\d+(:\d+)?$", title):
			titles.append(title)

elif url.find("cjsw.com") != -1:
	divs = soup.find_all('li', class_='chart__item')

	for d in divs:
		spans = d.find_all('span')
		titles.append(spans[0].string + ' - ' + spans[1].string.split(" • ")[0])

else:
	print("Cannot scrape given website: " + url)

titles = list(set(titles))

urls = []
with open('output.txt', 'w') as f:
	for title in titles:
		urls.append(["https://soundcloud.com/search/sounds?q="+urllib.parse.quote_plus(title).replace("+", " ")+"\n", "https://bandcamp.com/search?q="+urllib.parse.quote_plus(title).replace("+", " ")+"\n", "https://www.beatport.com/search?q="+urllib.parse.quote_plus(title).replace(" ", "+")+"\n"])
		f.write(title + "\n")
		for url in urls[-1]:
			f.write(url)
		f.write("\n")

if OPEN_BROWSER:
	for l in urls:
		for t in l:
			webbrowser.open(t)
		
		input("Press enter for next song")