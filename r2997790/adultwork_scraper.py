import requests
import time

api = 'https://api-sandbox.adultwork.com/v1'

class Profile(object):
	"""docstring for Profile"""
	def __init__(self, name, url, available, lastLogin, userID):
		super(Profile, self).__init__()
		self.name = name
		self.url = url
		self.available = available
		self.lastLogin = lastLogin
		self.userID = userID
		self.phone = None

	def getPhone(self):
		r = requests.get(api+'/profile/getProfileDetails?apiKey=<apiKey>&ReturnContact=true&userID='+str(self.userID))
		if r.status_code == 200:
			resp = r.json()
			contactInfo = resp['Contact']
			if contactInfo['HasMobileNumber']:
				self.phone = contactInfo['MobileNumber']
			else:
				self.phone = 'No number'


page = 1
profiles = []

while True:
	r = requests.get(api+'/search/searchProfiles?apiKey=<apiKey>&CountryID=158&GenderIDs=2&IsEscort=true&ProfilesPerPage=100&PageNumber='+str(page))
	if r.status_code == 200:
		resp = r.json()
		totalPages = resp['PageCount']
		count = 0
		length = len(resp['Profiles'])
		for p in resp['Profiles']:
			profile = Profile(p['Nickname'], p['ProfileURL'], p['AvailableTodayEscort'], p['LastLoggedIn'], p['UserID'])
			profile.getPhone()
			profiles.append(profile)
			count += 1
			print(str(count)+'/'+str(length)+' in page '+str(page)+' complete')

	print(str(page)+'/'+str(totalPages)+' complete')
	if page > totalPages:
		break

	page += 1

print('Writing output file')
with open(time.strftime("adultwork-%y%m%dT%H%M%S.csv"), 'w') as f:
	f.write('url,name,availableToday,phone,lastLogin\n')
	for profile in profiles:
		f.write(str(profile.url)+','+str(profile.name)+','+str(profile.available)+','+str(profile.phone)+','+str(profile.lastLogin)+'\n')
