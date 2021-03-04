import time
import configparser
import re
import os
from datetime import datetime

from selenium import webdriver

browser = webdriver.Chrome()

url = 'https://nitrogensports.eu/'
browser.get(url)

time.sleep(10)

browser.execute_script("document.evaluate('//*[@id=\"modal-welcome-login-button\"]', document).iterateNext().click()", browser.find_element_by_tag_name('body'))

time.sleep(0.5)

config = configparser.ConfigParser()
config.read('nitrogen2.ini')

browser.find_element_by_xpath("//*[@id=\"modal-account-login-username-textbox\"]").send_keys(config['nitrogensports']['username']) #username
browser.find_element_by_xpath("//*[@id=\"modal-account-login-password-textbox\"]").send_keys(config['nitrogensports']['password']) #password
browser.find_element_by_xpath("//*[@id=\"modal-account-login-button\"]").click() #login button

time.sleep(5)


lines = []
children = browser.find_elements_by_class_name("menu-item-sport")

for i in range(1, len(children)+1):
	print(children[i-1].text)
	sport = children[i-1].text
	children[i-1].click()
	time.sleep(0.5)
	leagues = children[i-1].find_elements_by_class_name('menu-item-league')
	for league in leagues:
		browser.execute_script("arguments[0].scrollIntoView(); window.scrollBy(0, -50);", league)
		time.sleep(1)
		league.click()
		league_name = league.find_elements_by_tag_name('a')[0].get_attribute('innerHTML')
		time.sleep(3)
		events_set = browser.find_elements_by_class_name('events-result-set')
		if len(events_set) > 0:
			events = events_set[0].find_elements_by_class_name('event')
			for event in events:
				inner = event.find_elements_by_class_name('event-participants')[0].get_attribute('innerHTML')
				title = re.sub("<span.*?</span>", "", inner)
				competitors = title.split(' vs ')
				if len(competitors) < 2:
					continue

				time_text = event.find_elements_by_class_name('event-time-text')[0].get_attribute('innerHTML')
				time_obj = datetime.strptime(time_text.strip(), "%A, %B %d, %Y %I:%M%p")
				rows = event.find_elements_by_class_name('event-row')

				bets_1 = "N/A"
				bets_2 = "N/A"
				over = "N/A"
				under = "N/A"
				draw = "N/A"

				all_bets_1 = []
				all_bets_2 = []
				all_over = []
				all_under = []
				all_draw = []
				for row in rows:
					participant = re.sub("<span.*?</span>", "", row.find_elements_by_class_name('event-participant')[0].get_attribute('innerHTML'))
					if participant.find('Over') != -1:
						all_over.extend(row.find_elements_by_tag_name('option'))
					elif participant.find('Under') != -1:
						all_under.extend(row.find_elements_by_tag_name('option'))
					elif participant.find('Draw') != -1:
						all_draw.extend(row.find_elements_by_tag_name('option'))
					elif participant.find(competitors[0].strip()) != -1:
						all_bets_1.extend(row.find_elements_by_tag_name('option'))
					elif participant.find(competitors[1].strip()) != -1:
						all_bets_2.extend(row.find_elements_by_tag_name('option'))

				if len(all_bets_1) > 0:
					bets_1 = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_bets_1)))
				if len(all_bets_2) > 0:
					bets_2 = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_bets_2)))
				if len(all_over) > 0:
					over = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_over)))
				if len(all_under) > 0:
					under = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_under)))
				if len(all_draw) > 0:
					draw = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_draw)))

				'''
				if len(rows) > 0:
					all_bets_1 = rows[0].find_elements_by_tag_name('option')
					if len(rows) > 5:
						all_bets_1.extend(rows[2].find_elements_by_tag_name('option'))
					bets_1 = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_bets_1)))
					all_bets_2 = rows[1].find_elements_by_tag_name('option')
					if len(rows) > 5:
						all_bets_2.extend(rows[3].find_elements_by_tag_name('option'))
					bets_2 = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_bets_2)))

					if len(rows) > 2:
						all_over = rows[-2].find_elements_by_tag_name('option')
						over = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_over)))
						all_under = rows[-1].find_elements_by_tag_name('option')
						under = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_under)))
					else:
						over = "N/A"
						under = "N/A"

					if len(rows) > 6:
						all_draw = rows[-3].find_elements_by_tag_name('option')
						draw = ":".join(list(map(lambda x: x.get_attribute('innerHTML'), all_draw)))
					else:
						draw = "N/A"
				else:
					bets_1 = "N/A"
					bets_2 = "N/A"
					over = "N/A"
					under = "N/A"
					draw = "N/A"
				'''

				lines.append(sport+","+league_name+","+time_obj.strftime("%m.%y.%d,%I:%M %p")+","+competitors[0].strip()+","+bets_1+","+competitors[1].strip()+","+bets_2+","+draw+","+over+","+under)
				print(lines[-1])
	

browser.close()

lines = list(set(lines))
lines.insert(0, 'sport,league,date,time,comp1,odds1,comp2,odds2,draw,over,under')
with open(time.strftime("nitrogensports-%y%m%dT%H%M%S.csv"), 'w') as f:
	for line in lines:
		f.write(line+'\n')