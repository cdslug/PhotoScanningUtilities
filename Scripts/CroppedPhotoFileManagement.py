import os
import sys
from os import listdir
from os.path import isfile, isdir, join
import shutil
from PIL import Image

def pairFileNames(fileNamesPrimary, fileNamesSecondary):
	pairedFileNames = []
	for namePrim in fileNamesPrimary:
		matched = False
		for indexSec,nameSec in enumerate(fileNamesSecondary):
			tailPrim = os.path.split(namePrim)[1][:-4]
			tailSec = os.path.split(nameSec)[1][:-4]
			if tailPrim in tailSec:
				pairedFileNames.append([namePrim,nameSec])
				matched = True
				#optimize the search by removing matched entries
				del fileNamesSecondary[indexSec]
				break
		if matched == False:
			pairedFileNames.append([namePrim,None])

	return pairedFileNames


def photoTransfer(fileNamePrim, fileNameSec):
	if fileNameSec == None:
		return
	else:
		os.remove(fileNamePrim)
		shutil.copyfile(fileNameSec,fileNamePrim)
		os.remove(fileNameSec)



def selectOptimalPhoto(primaryPath, secondaryPath):
#match photo files together
#select optimal photo
#remove unwanted photo
#copy over optimal photo if needed to primary directory


	fileNamesPrimary = []
	for (dirpath, dirnames, filenames) in os.walk(primaryPath):
		for fn in filenames:
			if fn[-4:].lower() in ['.jpg','.png']:
				fileNamesPrimary.append(os.path.join(dirpath,fn))
	fileNamesPrimary.sort()

	fileNamesSecondary = []
	for (dirpath, dirnames, filenames) in os.walk(secondaryPath):
		for fn in filenames:
			if fn[-4:].lower() in ['.jpg','.png']:
				fileNamesSecondary.append(os.path.join(dirpath,fn))
	fileNamesSecondary.sort()

	pairedFileNames = pairFileNames(fileNamesPrimary, fileNamesSecondary)
	# print "Photo files: " + str(onlyPhotoFile)
	wThresh = 3204
	hThresh = 2175
	whThresh = wThresh*hThresh
	wAverage = 0
	hAverage = 0
	usefulCount = 0
	for namePair in pairedFileNames:
		pixelsImagePrim = None
		pixelsImageSec = None

		img = Image.open(namePair[0])
		wPrim, hPrim = img.size
		pixelsImagePrim = wPrim*hPrim

		wSec = wPrim
		hSec = hPrim
		pixelsImageSec = pixelsImagePrim

		if namePair[1] != None:
			img = Image.open(namePair[1])
			wSec,hSec = img.size
			pixelsImageSec = wSec*hSec
			if wSec < wThresh * 0.95 or wSec > wThresh*1.05 or\
			   hSec < hThresh * 0.95 or hSec > hThresh*1.05:
				#os.remove(namePair[1])
				shutil.copyfile(namePair[0],namePair[1])
				namePair[1] = None
			else:
				wAverage += wSec
				hAverage += hSec
				usefulCount += 1

		print('{}\tw: {}\th: {}\tw*h: {}'.format(namePair[0][-30:],wSec,hSec,pixelsImageSec))
		if namePair[1] == None and (pixelsImageSec < whThresh * 0.95 or pixelsImagePrim > whThresh * 1.05):
			print('Investigate: {}'.format(namePair[0][-30:]))
			continue

		photoTransfer(*namePair)
	wAverage /= float(usefulCount)
	hAverage /= float(usefulCount)
	print('wAverage: {}\nhAverage: {}\nwhAverage: {}'.format(wAverage,hAverage,wAverage*hAverage))
	return


########################
#####     MAIN     #####
########################
if __name__ == "__main__":
	inputPathPrimary = sys.argv[1]
	inputPathSecondary = sys.argv[2]

	selectOptimalPhoto(inputPathPrimary, inputPathSecondary)
