from PIL import Image
import sys
from collections import Counter
import itertools
import webbrowser

def padded_hex(i):
	if i < 16:
		return '0' + hex(i)[2:]
	else:
		return hex(i)[2:]

if len(sys.argv) < 2:
	print('Usage: {sys.argv[0]} <image1> [<image2> ...]')
else:
	for i in range(1, len(sys.argv)):
		try:
			im = Image.open(sys.argv[i]).convert('RGB')
			rgb = im.load()
			sizes = im.size

			pixels = [rgb[p[0], p[1]] for p in itertools.product(range(0, sizes[0]), range(0, sizes[1]))]

			c = [padded_hex(t[0]) + padded_hex(t[1]) + padded_hex(t[2]) for t in [x[0] for x in Counter(pixels).most_common(5)]]
			for i in range(0, 5 - len(c)):
				c.append('ffffff')

			webbrowser.open('https://coolors.co/'+('-'.join(c)))
					
		except Exception as e:
			print('Invalid image file: ' + sys.argv[i])
			raise e
