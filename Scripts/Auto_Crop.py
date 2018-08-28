import RotationLog
import Rotate_Auto
import Rotate_Manual
import Crop
import cv2

import sys
import os
from multiprocessing import Process
import shutil
import time
import random


##TODO
##I just finished save thumbnail
##I need to move out some code from workPipelined with the filesIO
##I don't need the thumbnails actually
def countFiles(path):
	fileCount = 0

	if os.path.isfile(path):
		fileCount += 1
	else:
		for root, dirs,files in os.walk(path):
			fileCount += len([f for f in files if f[-4:].lower() in ['.jpg','.JPG','.png']])

	return fileCount

def getAllFiles(inputPaths):
	filePathsInput = []
	for f in inputPaths:
		if os.path.isfile(f):
			filePathsInput.append(f)
		elif os.path.isdir(f):
			for root, dirs, files in os.walk(f):
				#root must always have 'Scans' at the end

				for name in files:
						filePathsInput.append(os.path.join(root,name))
					# print name
	return filePathsInput


# def saveThumbnail(inputPath,thumbnailPath):
# 	if not os.path.isfile(thumbnailPath):
# 		#if there are more than <threshold> files to be rotate, run rotation script
# 		img = cv2.imread(inputPath)
# 	    thumbScale = 0.10
# 	    wThumb = int(img.shape[1]*thumbScale)
# 	    hThumb = int(img.shape[0]*thumbScale)
# 	    img = cv2.resize(img,(wThumb,hThumb)) #speed up for testing
# 		cv2.imwrite(thumbnailPath, img)

# def generateThumbnails(photoPaths):
# 	ip,tp,op,mp = photoPaths #input,thumbnail,output,manual
# 	saveThumbnail(ip,tp)

def mkdir_p(path):
	try:
		dirPath = path.split("/")
		dirPath = "/".join(dirPath[:-1])
		os.makedirs(dirPath)
	except OSError as exc:  # Python >2.5
		pass
		# if exc.errno == errno.EEXIST and os.path.isdir(path):
		# 	pass
		# else:
		# 	raise

def crop(filePaths):

	colorThreshold = 25
	acceptedRatios = [1.5,0.66,1]
	additionalCropRatio = 0.01
	for index,fileSet in enumerate(filePaths):
		#copy the directory structure that the file is in
		if not os.path.isfile(fileSet["Input"]):
			return
		mkdir_p(fileSet["Output"])
		mkdir_p(fileSet["Manual"])
		# mkdir_p(fileset["Thumbnail"])
		basename = os.path.basename(fileSet["Input"])
		name, ext = os.path.splitext(basename)
		print("{:.4f}% {} of {}: {}".format(index/float(len(filePaths)),index,len(filePaths),basename))

		if basename[0] == "." or ext.lower() not in [".jpg",".png"]:
			shutil.copy(fileSet["Input"],fileSet["Output"])
			return
		else:
			if not os.path.isfile(fileSet["Output"]) and not os.path.isfile(fileSet["Manual"]):
				img = cv2.imread(fileSet["Input"])
				img = Crop.rotate_image(img,colorThreshold)
				img, checkCropped = Crop.crop_image(img,
												   colorThreshold,
												   acceptedRatios,
												   additionalCropRatio)
				# cv2.imshow("cropped?: {}".format(checkCropped), img)
				# cv2.waitKey(0)
				if checkCropped == True:
					#save to Output
					cv2.imwrite(fileSet["Output"], img, [cv2.IMWRITE_JPEG_QUALITY, 100])
				else:
					#save to Manual
					shutil.copy(fileSet["Input"],fileSet["Manual"])

def executePipeline(filePaths):

	crop(filePaths)
	# procs = []
	# numProcs = 8
	# step = len(filePaths)/numProcs +1
	# for index in range(numProcs):
	# 	### cluster in separate folder chuncks
	# 	# p = Process(target = map,args = (generateThumbnails,filePaths[index*step:index*step+step]))
	#
	# 	#cluster so close files are worked on in parallel
	# 	p = Process(target = map,args = (crop,[filePaths[index::numProcs]]))
	#
	# 	p.start()
	# 	procs.append(p)
	#
	# for p in procs:
	# 	p.join()

if __name__ == '__main__':
	inputPaths = getAllFiles(sys.argv[1:])
	# inputPaths.sort()
	random.shuffle(inputPaths)

	#Get the path of the directory to mimic
	basePath = sys.argv[1]
	basePath = basePath[:basePath.index('SCANS') + len('SCANS')]

	#create job stats files
	statsFile = os.path.join(basePath,'CropStats.csv')
	if not os.path.isfile(statsFile):
		with open(statsFile,'w') as sf:
			sf.write('AutoCropped,NotCropped\n')

	#create mirror paths in the working directories
	filePaths = []
	for path in inputPaths:
		inputPath = path
		thumbnailPath = path.replace('SCANS','SCANS_CropThumbnail')
		outputPath = 	path.replace('SCANS','SCANS_CropDone')
		manualPath = 	path.replace('SCANS','SCANS_CropManual')
		filePaths.append({  "Input": inputPath,
					 		"Thumbnail":thumbnailPath,
					 		"Output": outputPath,
					 		"Manual": manualPath
					 	 })
	# print("filePaths[:10] {}".format(filePaths[:10]))

	print("starting job of {} files".format(len(filePaths)))
	timeStart = time.time()
	executePipeline(filePaths)
	timeStop = time.time()
	print("### time taken = {}".format(timeStop-timeStart)) #2.33s

	#
	# with open(statsFile,'a') as sf:
	# 	sf.write('{0},{1},{2}\n'.format(autoCropCount,notCroppedCount))
