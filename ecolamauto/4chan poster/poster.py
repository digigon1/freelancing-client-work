from selenium import webdriver
import requests
from time import sleep
import configparser

config = configparser.ConfigParser()
config.read("poster.cfg")

browser = webdriver.Chrome()

API_KEY = config.get("Keys", "2captcha")  # Your 2captcha API KEY
url = 'https://boards.4chan.org/biz/'
browser.get(url)

subject = 'test'
comment = 'comment'
file_to_send = ''  # absolute path to file

browser.find_element_by_id("togglePostFormLink").click()
browser.find_element_by_name("sub").send_keys(subject)
browser.find_element_by_name("com").send_keys(comment)
browser.find_element_by_name("upfile").send_keys(file_to_send)

s = requests.Session()

site_key = browser.execute_script("return window.recaptchaKey")

# here we post site key to 2captcha to get captcha ID (and we parse it here too)
captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key, url)).text.split('|')[1]
# then we parse gresponse from 2captcha response
recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
print("solving ref captcha...")
while 'NOT_READY' in recaptcha_answer:
    sleep(5)
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
recaptcha_answer = recaptcha_answer.split('|')[1]

browser.execute_script("document.getElementById('g-recaptcha-response').style.display = ''")
response = browser.find_element_by_id("g-recaptcha-response")
response.send_keys(recaptcha_answer)

browser.find_element_by_xpath('//*[@id="postForm"]/tbody/tr[3]/td[2]/input[2]').click()

browser.close()
