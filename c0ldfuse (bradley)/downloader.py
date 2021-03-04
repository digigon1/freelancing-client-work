import os
import urllib.request

from PIL import Image

pages = ['profile', 'boat-deck', 'a-deck', 'b-deck', 'c-deck', 'd-deck', 'e-deck', 'f-deck', 'g-deck', 'orlop-deck', 'tank-top']

if not os.path.exists('results'):
	os.makedirs('results')

for location in pages:
	i = 1
	while True:
		try:
			request = urllib.request.Request('https://www.encyclopedia-titanica.org/titanic-deckplans/'+location+'/TileGroup0/'+str(i)+'-0-0.jpg', method='HEAD')
			request.add_header('User-agent', 'Chrome XXX')
			urllib.request.urlopen(request)
		except Exception as e:
			break
	
		i += 1
	
	i -= 1

	max1 = 0
	while True:
		try:
			request = urllib.request.Request('https://www.encyclopedia-titanica.org/titanic-deckplans/'+location+'/TileGroup0/'+str(i)+'-'+str(max1)+'-0.jpg', method='HEAD')
			request.add_header('User-agent', 'Chrome XXX')
			urllib.request.urlopen(request)
		except Exception as e:
			break
	
		max1 += 1

	max2 = 0
	while True:
		try:
			request = urllib.request.Request('https://www.encyclopedia-titanica.org/titanic-deckplans/'+location+'/TileGroup0/'+str(i)+'-0-'+str(max2)+'.jpg', method='HEAD')
			request.add_header('User-agent', 'Chrome XXX')
			urllib.request.urlopen(request)
		except Exception as e:
			break
	
		max2 += 1
	
	if not os.path.exists('results/'+location):
		os.makedirs('results/'+location)

	print('Downloading '+location)
	for x in range(0,max1):
		for y in range(0,max2):
			tries = 0
			while tries < 5:
				try:
					request = urllib.request.Request('https://www.encyclopedia-titanica.org/titanic-deckplans/'+location+'/TileGroup0/'+str(i)+'-'+str(x)+'-'+str(y)+'.jpg', method='GET')
					request.add_header('User-agent', 'Chrome XXX')
					r = urllib.request.urlopen(request)
					f = open('results/'+location+'/'+str(i)+'-'+str(x)+'-'+str(y)+'.jpg', 'wb')
					f.write(r.read())
					f.close()
					break
				except Exception as e:
					tries += 1

	total_width = 0
	for x in range(0,max1):
		total_width += Image.open('results/'+location+'/'+str(i)+'-'+str(x)+'-0.jpg').size[0]

	total_height = 0
	for y in range(0,max2):
		total_height += Image.open('results/'+location+'/'+str(i)+'-0-'+str(y)+'.jpg').size[1]

	new_img = Image.new('RGB', (total_width, total_height), "white")
	
	print('Creating full image')
	x_offset = 0
	for x in range(0,max1):
		y_offset = 0
		for y in range(0,max2):
			try:
				im = Image.open('results/'+location+'/'+str(i)+'-'+str(x)+'-'+str(y)+'.jpg')
				new_img.paste(im, (x_offset, y_offset))
				y_offset += im.size[1]
			except Exception as e:
				break
		x_offset += Image.open('results/'+location+'/'+str(i)+'-'+str(x)+'-0.jpg').size[0]

	new_img.save('results/'+location+'.jpg')