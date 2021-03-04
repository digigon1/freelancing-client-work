import time

from selenium import webdriver

browser = webdriver.Chrome()

url = 'https://sportsbet.io'
browser.get(url)

time.sleep(10)

browser.execute_script("document.evaluate('//*[@id=\"1\"]', document).iterateNext().click()", browser.find_element_by_tag_name('body'))
browser.execute_script("document.evaluate('//*[@id=\"1\"]', document).iterateNext().click()", browser.find_element_by_tag_name('body'))

lines = []
for div in [1, 2]:
	full_list = browser.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/ul["+str(div)+"]")
	children = full_list.find_elements_by_tag_name("li")
	if div == 1:
		children.pop()
	


	for i in range(1, len(children)+1):
		print(children[i-1].text)
		try:
			browser.execute_script("document.evaluate('/html/body/div[1]/div[2]/div[1]/div/ul["+str(div)+"]/li["+str(i)+"]', document).iterateNext().click()", children[i-1])
			time.sleep(5)
			competitions = browser.find_elements_by_xpath('//div[@class="event-container"]')
			for comp in competitions:
				game_time = comp.find_elements_by_class_name('start')[0].find_elements_by_tag_name('div')[0].text.split('\n')
				d = game_time[0]
				t = game_time[1]
				competitors = comp.find_elements_by_class_name('competitors')[0].text.split(' V ')
				odds = comp.find_elements_by_class_name('odds')
				extra = comp.find_elements_by_class_name('extra-odds')[0].text
				lines.append((children[i-1].text+','+d+','+t+','+competitors[0]+','+odds[0].text+','+competitors[1]+','+odds[2].text+','+extra))
		except Exception as e:
			print(e)
	
browser.close()

lines = list(set(lines))
lines.insert(0, 'sport,date,time,comp1,odds1,comp2,odds2,extra odds')
with open(time.strftime("sportsbet-%y%m%dT%H%M%S.csv"), 'w') as f:
	for line in lines:
		f.write(line+'\n')