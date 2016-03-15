import sys
import os
from os import listdir
from os.path import isfile, isdir, join
import shutil
from PIL import Image

def checkInputArgs(numInputs):
	if len(sys.argv) != numInputs + 1:
		sys.exit("Error: Incorrect usage. Script requires " + str(numInputs) + " input arguments.")

def prepareDirectories(name, inputPath):
	#Input:
	#	name: name of desired directory
	#	inputPath: path to prepare the desired directory
	#Output:
	#	resultingPath: inputPath appended with name of desired directory

	### check if the base path exists
	if not os.path.exists(inputPath):
		sys.exit("Error: " + inputPath + " does not exist")

	resultingPath = inputPath + "/" + name
	
	### There's a possiblity for a race condition
	### but it's unlikely these directories will be deleted immediately after checking if they exist
	if not os.path.exists(resultingPath):
		try:
			os.makedirs(resultingPath)
		except OSError:
			sys.exit("Error: could not create " + resultingPath + \
					 "\nCheck permissions.")

	return {'resultingPath': resultingPath}

def getNextFolderNumber(workingDir, folderPrefix):
	onlyDir = [d for d in listdir(workingDir) if isdir(join(workingDir, d))]
	#runtime error if not in the format "folderPrefix_###"
	#TODO: make more robust if the directory naming format is not consistent
	dirNameNumList = [int(d.split("_")[1]) for d in onlyDir if folderPrefix in d]
	# print "dirN"
	nextNum = 1
	if dirNameNumList != []:
		nextNum = max(dirNameNumList) + 1
	print "Next folder number = " + str(nextNum)
	return nextNum

def separatePhotos(workingDir, folderPrefix):
	#known issues: if there is an error while in this function, a photo folder will be segmented
	inputPath = prepareDirectories("NEWSCANS_Rotated", workingDir)["resultingPath"]
	nextFolderNumber = getNextFolderNumber(workingDir, folderPrefix)
	outputPath = ''
	print "# files = " + str(len(listdir(inputPath)))
	fileNames = [f for f in listdir(inputPath) if isfile(join(inputPath, f)) and f[-4:].lower() in ['.jpg','.png']]
	fileNames.sort()

	# print "Photo files: " + str(onlyPhotoFile)
	sizeThresh = 350000 
	whThresh = 3287 * 2624
	for name in fileNames:
		photoFileFullPathOld = join(inputPath,name)
		isPhotoFile = name[-4:] in ['.jpg','.png']
		ratioThresh = ratioImage = None
		if isPhotoFile:
			img = Image.open(photoFileFullPathOld)
			w,h = img.size
			ratioThresh = 1.2*(sizeThresh/float(whThresh))
			ratioImage = os.path.getsize(photoFileFullPathOld)/float(w*h)
			print '{0}\t vs {1}'.format(ratioImage,ratioThresh)
		if ratioImage >= ratioThresh or isPhotoFile == False:
			#only create a new folder if there is a file to copy into it
			if outputPath == '':
				outputPath = prepareDirectories(folderPrefix + "_" + str(nextFolderNumber).zfill(3), workingDir)["resultingPath"]
				nextFolderNumber += 1
		else:
			print "Separate file detected"
			outputPath = ''

		if outputPath != '':
			shutil.copyfile(photoFileFullPathOld,join(outputPath,name))
			os.remove(photoFileFullPathOld)
		# os.remove(photoFileFullPathOld)
	#should not be true if a new folder is only created if there is a photo to copy to it
	if outputPath != [] and len(listdir(outputPath)) == 0:
		shutil.rmtree(outputPath)
	return


########################
#####     MAIN     #####
########################
# 	prepare newfolder directory
#	Determine largest number-suffix of the provided folder prefix (n-1)
#	Create a new folder with: folderprefix_00n
#  	Iterate through all photo files
#  		if a file is >= than the threshold size:
#			save the photo file to the prepared folder
#		else if the file is < the threshold size:
#			this is the end of the batch, create a new folder
#		
checkInputArgs(2)
workingDir = sys.argv[1]
folderPrefix = sys.argv[2]


separatePhotos(workingDir, folderPrefix)
