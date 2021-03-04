import time

from selenium import webdriver

browser = webdriver.Chrome()

url = 'http://www.sobeys.com/en/flyer/'
browser.get(url)

time.sleep(15)

browser.switch_to.frame(browser.find_element_by_id('flipp-iframe'))

browser.find_element_by_xpath('//div[@role="button" and contains(@class, "wishabi-broadsheettopbar-grid-view")]').click()
time.sleep(10)

lines = []
items = browser.find_elements_by_class_name('item')
for item in items:
	price = item.find_elements_by_class_name('item-price')[0].text
	if price.strip() != "":
		name = item.find_elements_by_class_name('item-name')[0].text
		lines.append(name+","+price)

browser.close()

lines = list(set(lines))
lines.insert(0, 'product,price')
with open(time.strftime("sobeys-%y%m%dT%H%M%S.csv"), 'w') as f:
	for line in lines:
		f.write(line+'\n')