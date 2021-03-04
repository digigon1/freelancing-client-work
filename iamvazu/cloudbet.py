import requests
import time

lines = ['comp,time,name,over,under,1x2,hdp1,hdp2,extra props']
for game in range(1,37):

	r = requests.get('https://www.cloudbet.com/api/v2/sports/asian_events/'+str(game)+'?from=0&to=2501819200', headers={'Accept': 'application/json'})
	if r.status_code == 200:
		resp = r.json()
		try:
			for event in resp['events']:
				com = event['competition']['name']
				t = time.gmtime(event['starts_at'])
				comps = event['competitors']
				if len(comps) != 2:
					#continue
					pass
				name = comps[0]['name']+' vs '+comps[1]['name']
				#print(name+':')
				try:
					over = ''
					under = ''
					oneXtwo1 = ''
					oneXtwo2 = ''
					hdp1 = ''
					hdp2 = ''

					for market in event['markets']:
						odds = ['', '']
						index = None
						for odd in market['selections']:
							underBool = False
							try:
								if odd['type'] == 'Under' or odd['type'] == 'Over':
									underBool = True
									if odd['type'] == 'Under':
										index = 0
									else:
										index = 1
								else:
									index = int(odd['type']) - 1
								#print(odd['type'])
							except Exception as e:
								index = 0
							
							try:
								o = odd['odds']
								o -= 1.;
								odds[index] += odd['special_bet_value'] + ':'
								if o < 1:
									odds[index] += ('-' + str(int(100/o)))
								else:
									odds[index] += ('+' + str(int(o*100)))
			
								odds[index] += ';'
							except Exception as e:
								o = odd['odds']
								o -= 1.;
								if o < 1:
									odds[index] += ('-' + str(int(100/o)))
								else:
									odds[index] += ('+' + str(int(o*100)))
			
								odds[index] += ' '
						
						odds[0] = odds[0][:-1]
						odds[1] = odds[1][:-1]
	
						if underBool:
							over = odds[0]
							under = odds[1]
						elif ':' in odds[0]:
							hdp1 = odds[0]
							hdp2 = odds[1]
						else:
							oneXtwo1 = odds[0]
							oneXtwo2 = odds[1]
	
					lines.append(com.replace(',','').strip() + ','+time.strftime("%m.%y.%d %I:%M %p", t)+','+name+','+over+','+under+','+oneXtwo1 + ' x ' + oneXtwo2+','+hdp1+','+hdp2+','+str(hdp1.count(':')))
	
				except Exception as e:
					#print('No odds found')
					#print(e)
					#raise e
					pass

				#print()
		except Exception as e:
			#continue
			#print(e)
			#raise e
			pass
	else:
		print(str(r.status_code))


with open(time.strftime("cloudbet-%y%m%dT%H%M%S.csv"), 'w') as f:
	for line in lines:
		f.write(line+'\n')