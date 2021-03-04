import MySQLdb
import csv

db = MySQLdb.connect('host', 'user', r'password', 'database')

with open('cik_ticker.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile)
	skip = True
	for row in spamreader:
		if skip:
			skip = False
			continue
		while True:
			cursor = db.cursor()
			if row[0] != '':
				try:
					cursor.execute("""INSERT INTO cik (cik, ticker) VALUES (%s, %s)""", (row[0], row[1]))
				except Exception as e:
					print(e)
					db = MySQLdb.connect('host', 'user', r'password', 'database')
					continue
			break
