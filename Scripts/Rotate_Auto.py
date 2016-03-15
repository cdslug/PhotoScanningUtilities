import os
import sys
import numpy as np
import cv2 
from PIL import Image
import numpy
import errno
import shutil
from multiprocessing import Process
import inspect

import Rotate
import RotationLog
import Rotate_Manual

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def haarDetect(imgCV2,classifierPath):

	objectCascade = cv2.CascadeClassifier(classifierPath)
	rows,cols,foobar = imgCV2.shape
	matchedOrientations = [0]*4
	for n in range(4):
		M = cv2.getRotationMatrix2D((cols/2,rows/2),n*90,1)
		rotImg = cv2.warpAffine(imgCV2,M,(cols,rows))
		gray = cv2.cvtColor(rotImg, cv2.COLOR_BGR2GRAY)

		objects = objectCascade.detectMultiScale(gray, 1.3, 5)
		if objects != []:
			matchedOrientations[n] = len(objects)

	return matchedOrientations

def autoRotate(inputPath, outputPath):

	imgOrigPIL = Image.open(inputPath)
	imgThumbPIL = imgOrigPIL.copy()

	autoDetectSize = 300
	if max(imgOrigPIL.size) > autoDetectSize:
		imgThumbPIL.thumbnail((autoDetectSize,autoDetectSize), Image.ANTIALIAS)
	size = imgThumbPIL.size
	width,height = size
	dim = max(size)

	imgSqPIL = Image.new('RGB',(dim,dim))
	imgSqPIL.paste(imgThumbPIL,(dim/2-width/2,dim/2-height/2))

	imgCV2 = numpy.array(imgSqPIL)
	imgCV2 = imgCV2[:,:,::-1].copy()

	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	classifierPaths = [	os.path.join(scriptPath,'haarcascades/haarcascade_frontalface_default.xml'),
						os.path.join(scriptPath,'haarcascades/haarcascade_frontalface_alt.xml'),
						os.path.join(scriptPath,'haarcascades/haarcascade_profileface.xml')
						# os.path.join(scriptPath,'haarcascades/HS.xml)'
						# os.path.join(scriptPath,'haarcascades/haarcascade_fullbody.xml)',
						# os.path.join(scriptPath,'haarcascades/haarcascade_upperbody.xml)',
						# os.path.join(scriptPath,'haarcascades/haarcascade_frontalcatface.xml)',
						# os.path.join(scriptPath,'haarcascades/haarcascade_frontalcatface_extended.xml)'
						]
	matchedOrientations = []
	for cp in classifierPaths:
		matchedOrientations.append(haarDetect(imgCV2,cp))

	matchCounts = zip(*matchedOrientations)
	temp = [sum(c) for c in matchCounts]
	# print '{0} temp={1}'.format(outputPath.split('/')[-1],temp)
	likelyOrientation = temp.index(max(temp)) if temp.count(max(temp)) == 1 else None

	if likelyOrientation != None:
		# print '{0} rotated {1} * 90'.format(outputPath,likelyOrientation)
		imgOrigPIL = imgOrigPIL.rotate(likelyOrientation*90,expand=True)
		imgOrigPIL.save(outputPath,'JPEG',quality=100)
		return True
	else:
		return False


def saveThumbnail(inputPath,outputPath):
	imgOrigPIL = Image.open(inputPath)
	imgThumbPIL = imgOrigPIL.copy()

	thumbSize = 500,500
	imgThumbPIL.thumbnail(thumbSize, Image.ANTIALIAS)
	# thumbPath = '/'.join(inputPath.split('/')[:-1]).replace('SCANS','SCANS_RotThumb')
	thumbPath = outputPath
	mkdir_p(thumbPath)
	thumbPath = os.path.join(thumbPath,inputPath.split('/')[-1])
	imgThumbPIL.save(thumbPath,'JPEG',quality=80)

	#if there are more than <threshold> files to be rotate, run rotation script


def rotateImage(photoPaths):

	inputPath,outputPath = photoPaths

	if autoRotate(inputPath,outputPath) == True:
		pass
		# RotationLog.appendRotationLog([inputPath])
	
	outputThumbPath = '/'.join(inputPath.replace('SCANS/','SCANS_RotThumb/').split('/')[:-1])
	saveThumbnail(inputPath,outputThumbPath)
	#write file name to text file in rotated image directory

def rotatePipelined(fileList):
	### this python Automator script requires the watched directory to end with 'SCANS'
	for f in fileList:
		if 'SCANS' in f:
			# print 'fuck {}'.format(f)
			filePathsInput = []
			if os.path.isfile(f):
				filePathsInput.append(f)
				mkdir_p('/'.join(f.replace('SCANS/','SCANS_Rotated/').split('/')[:-1]))
				mkdir_p('/'.join(f.replace('SCANS/','SCANS_RotThumb/').split('/')[:-1]))
			else:
				for root, dirs, files in os.walk(f):
					#root must always have 'SCANS' at the end
					mkdir_p(root[:-4] + root[-4:].replace('SCANS','SCANS_Rotated'))
					mkdir_p(root[:-4] + root[-4:].replace('SCANS','SCANS_RotThumb'))
					for name in files:
						filePathsInput.append(os.path.join(root,name))
					# for name in dirs:
						# print '### {0} ###'.format(os.path.join(root,name).replace('SCANS','SCANS_Rotated'))
					
			# print 'filePathsInput: {0}'.format(filePathsInput)
			filePathsOutput = []

			for path in filePathsInput:
				#not robust, but very easy to implement
				#fails if there are sub-folders with the same name as a parent
				op = path.replace('SCANS','SCANS_Rotated')
				filePathsOutput.append(op)
				### if not a supported file type transfer without question, don't want to lose it
				if path[-4:] not in ['.jpg','.png'] and path.split('/')[-1][0] != '.':
					shutil.copy(path,op)
			filePathsIO = zip(filePathsInput,filePathsOutput)
			filePathsIO = [(i,o) for (i,o) in filePathsIO if i[-4:] in ['.jpg','.png'] and i.split('/')[-1][0] != '.']

			procs = []
			numProcs = 4
			step = len(filePathsIO)/numProcs +1
			for index in range(numProcs):
				p = Process(target = map,args = (rotateImage,filePathsIO[index*step:index*step+step]))
				p.start()
				procs.append(p)

			for p in procs:
				p.join()

			

	# return fileList[1]


if __name__ == '__main__':
	baseInputPath = sys.argv[1]
	baseInputPath = baseInputPath[:baseInputPath.index('SCANS') + len('SCANS')]
	baseRotatedPath = baseInputPath + '_Rotated'
	#depends on the behavior that hidden files starting with '.' are not copied over to other folders
	filesRotated = RotationLog.getRotationLog(baseRotatedPath)
	# print('files Rotated: {0}'.format(filesRotated))
	filesUnrotated = RotationLog.checkUnrotatedFiles(filesRotated,sys.argv[1:])
	# print 'Files Not Rotated Yet: {0}'.format(filesUnrotated)
	rotatePipelined(filesUnrotated)

	###Rotate Manual at end so files to be rotated are the same
	# Rotate_Manual.filesUnrotated = [f.replace('SCANS/','SCANS_RotThumb/') for f in filesUnrotated]

	# 	# print '###filesUnrotated: {0}'.format(filesUnrotated)
	# Rotate_Manual.manualRotate(filesUnrotated)


		
	


			
			