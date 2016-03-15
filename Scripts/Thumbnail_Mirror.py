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
		maxDim = max(w,h)
		ratio = maxSize/float(maxDim)
		wSmall = int(w*ratio)
		hSmall = int(h*ratio)
		im.thumbnail((wSmall,hSmall),Image.ANTIALIAS)

		# w, h = im.size
		# im = im.crop((w/2-maxSize/2, h/2-maxSize/2, w/2 + maxSize/2, h/2 + maxSize/2))
	
	photoName = photoPath['Input'].split('/')[-1]
	photoName = photoName.replace('jpg','png')
	photoName = photoName.replace(' ','_') #opencv doens't like spaces in  names
	#keys should be called in this order

	saveFormat = {'JPG':'JPEG','PNG':'PNG'}
	outputPath = photoPath['Output']
	fileExt = outputPath[-3:].upper()
	im.save(outputPath,saveFormat[fileExt],quality = 100)

	return

def findPhotoPaths(inputPath):
	photoPaths = []
	#if directory, handle recursively
	if os.path.isdir(inputPath):
		for path in [os.path.join(inputPath,p) for p in os.listdir(inputPath)]:
			if os.path.isdir(path):
				photoPaths += findPhotoPaths(path)
			elif os.path.isfile(path) and path[-4:] in ['.jpg','.png'] and path.split('/')[-1][0] != '.':
				photoPaths.append(path)
	#if photo, add to list by returning
	elif inputPath[-4:] in ['.jpg','.png']:
		photoPaths.append(inputPath)

	return photoPaths

def preparePhotoOutputPath(filePath):
	pathBuildup = []
	pathParts = filePath.split('/')
	pathStack = []
	###paths must be for photo files
	if pathParts[-1][-4:] in ['.jpg','.png']:
		#ignore the filename, only interested in creating directories
		pathParts.pop()
		for index in reversed(range(len(pathParts))):
			#if directory path not found, add it to the stack to be created
			if not os.path.exists('/'.join(pathParts[:index+1])):
				pathStack.append('/'.join(pathParts[:index+1]))
			else: #if the path exists, then don't keep checking further back in the path
				break
	while len(pathStack) > 0:
		### There's a possiblity for a race condition
		### but it's unlikely these directories will be deleted immediately after checking if they exist
		path = pathStack.pop()
		try:
			os.makedirs(path)
		except OSError:
			sys.exit('Error: could not create {}\nCheck permissions.'.format(path))



def dumbFunc(maxSize,pathList):
	for pl in pathList:
		thumbnail(maxSize,pl)

if __name__ == '__main__':
	assert sys.argv[1].isdigit(), 'Input Error: maxSize must be a positive integer'
	maxSize = 		sys.argv[1]
	inputPath = 	sys.argv[2]
	outputPath = 	sys.argv[3]

	maxSize = int(maxSize)

	photoPathsInput = findPhotoPaths(inputPath)
	photoPathsOutput = []

	inputPathBase = inputPath if os.path.isdir(inputPath) else '/'.join(inputPath.split('/')[:-1])
	outputPathBase = outputPath

	for path in photoPathsInput:
		#not robust, but very easy to implement
		#fails if there are sub-folders with the same name as a parent
		op = outputPathBase + path[len(inputPathBase):]
		preparePhotoOutputPath(op)
		photoPathsOutput.append(op)

	photoPathsZip = zip(photoPathsInput,photoPathsOutput)
	photoPathsIO = [{'Input':i,'Output':o} for (i,o) in photoPathsZip]

	# dumbFunc(maxSize,paths)
	procs = []
	numProcs = 8
	step = len(photoPathsIO)/numProcs +1
	for index in range(numProcs):
		p = Process(target = dumbFunc,args = (maxSize,photoPathsIO[index*step:index*step+step]))
		p.start()
		procs.append(p)

	for p in procs:
		p.join()
