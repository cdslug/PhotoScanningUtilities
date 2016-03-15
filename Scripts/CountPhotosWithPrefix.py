import os
import sys

def checkInputArgs(numInputs):
	if len(sys.argv) != numInputs + 1:
		sys.exit("Error: Incorrect usage. Script requires " + str(numInputs) + " input arguments.")

def countPhotos(inputPath,folderPrefix):
	photoCount = 0

	if os.path.isdir(inputPath):
		listing = os.listdir(inputPath)
		for subitem in listing:
			if os.path.isdir(os.path.join(inputPath,subitem)) and folderPrefix in subitem:
				photoCount += countPhotos(os.path.join(inputPath,subitem),folderPrefix)
			else:
				photoCount += 1
	else:
		photoCount += 1

	return photoCount
		

if __name__ == '__main__':
	checkInputArgs(2)
	workingDir = sys.argv[1]
	folderPrefix = sys.argv[2] if len(sys.argv) == 3 else ''

	photoCount = countPhotos(workingDir,folderPrefix)
	print '{} photos in folders with prefix \'{}\''.format(photoCount,folderPrefix)

