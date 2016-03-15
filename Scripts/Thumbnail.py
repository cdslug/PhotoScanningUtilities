import os
import sys
from PIL import Image

def thumbnail(maxSize, photoPath):
	#resizees and crops a square of the middle of the image
	#photoPath is a diction with keys 'Input' and 'Output' with file path values
	im = Image.open(photoPath['Input'])
	w, h = im.size
	minSize = min(w,h)
	ratio = maxSize/float(minSize)
	wSmall = int(w*ratio)
	hSmall = int(h*ratio)
	im.thumbnail((wSmall,hSmall),Image.ANTIALIAS)

	w, h = im.size
	im = im.crop((w/2-maxSize/2, h/2-maxSize/2, w/2 + maxSize/2, h/2 + maxSize/2))
	
	outputPath = photoPath['Output'].split('.')[0]+'.png'
	im.save(outputPath,'PNG',quality = 100)

	return

if __name__ == '__main__':
	assert sys.argv[1].isdigit(), 'Input Error: maxSize must be a positive integer'
	maxSize = 		sys.argv[1]
	inputPath = 	sys.argv[2]
	outputPath = 	sys.argv[3]

	maxSize = int(maxSize)

	albumPathList = [{	'Input':os.path.join(inputPath, a),
						'Output':os.path.join(outputPath, a)
					 } 
						for a in os.listdir(inputPath)]

	for albumPath in albumPathList:
		# print albumPath['Input']
		# print os.path.isdir(albumPath['Input'])
		if os.path.isdir(albumPath['Input']):
			if not os.path.exists(albumPath['Output']):
				os.makedirs(albumPath['Output'])

			photoPathList = [{	'Input':os.path.join(albumPath['Input'],p),
								'Output':os.path.join(albumPath['Output'],p)
							 }
								 for p in os.listdir(albumPath['Input'])]
			#allow undoing a mistake, except for last photo
			photoPathOld = {}

			for photoPath in photoPathList:
				# print photoPath
				# print photoPath['Input'].split('/')[-1]
				if photoPath['Input'].split('/')[-1][0] != '.' and photoPath['Input'][-4:] == '.jpg':

					thumbnail(maxSize,photoPath)

	