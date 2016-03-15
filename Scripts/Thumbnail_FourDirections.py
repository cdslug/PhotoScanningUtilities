import os
import sys
from PIL import Image
from Queue import Queue
from threading import Thread
from multiprocessing import Process

# class ThumbnailWorker(Thread):
# 	def __init_(self, queue):
# 		Thread.__init__(self)
# 		self.queue = queue

# 	def run(self):
# 		while True:
# 			maxSize, photoPath, queue = self.queue.get()
# 			thumnailFolder(maxSize,photoPath,queue)
# 			self.queue.task_done()


def thumbnail(maxSize, photoPath):
	#resizees and crops a square of the middle of the image
	#photoPath is a diction with keys 'Input' and 'Output' with file path values
	im = Image.open(photoPath['Input'])
	if im.size != (maxSize,maxSize):
		w, h = im.size
		minSize = min(w,h)
		ratio = maxSize/float(minSize)
		wSmall = int(w*ratio)
		hSmall = int(h*ratio)
		im.thumbnail((wSmall,hSmall),Image.ANTIALIAS)

		w, h = im.size
		im = im.crop((w/2-maxSize/2, h/2-maxSize/2, w/2 + maxSize/2, h/2 + maxSize/2))
	
	photoName = photoPath['Input'].split('/')[-1]
	photoName = photoName.replace('jpg','png')
	photoName = photoName.replace(' ','_') #opencv doens't like spaces in  names
	#keys should be called in this order
	for key in ['Left','Down','Right','Up']:
		# print photoPath['Output']
		im = im.rotate(90)
		outputPath = os.path.join(photoPath['Output'][key], photoName)
		im.save(outputPath,'PNG',quality = 100)

	return

def thumbnailFolders(maxSize,photoPath):
	photoFormats = ['.jpg','.png']

	if os.path.isdir(photoPath['Input']):
		print photoPath['Input']

		for subPath in os.listdir(photoPath['Input']):
			newPhotoPath = {	'Input':os.path.join(photoPath['Input'], subPath),
								'Output': photoPath['Output']
							}
			thumbnailFolders(maxSize,newPhotoPath)

	elif photoPath['Input'].split('/')[-1][0] != '.' and photoPath['Input'][-4:] in photoFormats:
		thumbnail(maxSize,photoPath)

def findPhotoPaths(inputPath):
	photoPaths = []
	#if directory, handle recursively
	if os.path.isdir(inputPath):
		for path in os.listdir(inputPath):
			if os.path.isdir(path):
				photoPaths += findPhotoPaths(path)
			else:
				photoPaths += path
	#if photo, add to list by returning
	else if path[-4:] in ['.jpg','.png']:
		photoPaths += inputPath

	return photoPaths


	
	else:

	return photoPaths
def dumbFunc(maxSize,pathList):
	for pl in pathList:
		thumbnailFolders(maxSize,pl)

if __name__ == '__main__':
	assert sys.argv[1].isdigit(), 'Input Error: maxSize must be a positive integer'
	maxSize = 		sys.argv[1]
	inputPath = 	sys.argv[2]
	outputPath = 	sys.argv[3]

	maxSize = int(maxSize)

	photoPath = {	'Input':inputPath,
					'Output':{	'Up':os.path.join(outputPath,'Up'),
								'Right':os.path.join(outputPath,'Right'),
								'Down':os.path.join(outputPath,'Down'),
								'Left':os.path.join(outputPath,'Left')
							}
				}
	for op in photoPath['Output'].values():
		if not os.path.exists(op):
				os.makedirs(op)
	
	paths = [{'Input':os.path.join(photoPath['Input'],sp),'Output':photoPath['Output']} for sp in os.listdir(photoPath['Input'])]
	# dumbFunc(maxSize,paths)
	procs = []
	numProcs = 8
	step = len(paths)/numProcs 
	for index in range(numProcs):
		p = Process(target = dumbFunc,args = (maxSize,paths[index*step:index*step+step]))
		p.start()
		procs.append(p)

	for p in procs:
		p.join()
