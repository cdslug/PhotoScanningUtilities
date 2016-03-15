#!/usr/bin/env python
import os
import sys
from PIL import Image
import shutil
from multiprocessing import Process

import Rotate
import RotationLog

def pilSaveHelper(imgPIL,outputPath):
	imgPIL.save(outputPath,'JPEG',quality = 100)

def handleImage(photoPath):
	returnOrientation = []
	photoOrientation = None

	photoOrientation = Rotate.askPhotoOrientation(photoPath['InputThumb'])

	if photoOrientation.isdigit():
		# imageRotated = Image.open(photoPath['InputOriginal']).rotate(int(photoOrientation) * 90,expand=True)
		# shutil.copyfile(photoPath['Input'],photoPath['Processed'])
		# if photoOrientation == '0':
		# 	# shutil.copyfile(photoPath['InputOriginal'],photoPath['Output'])
		# 	p = Process(target = shutil.copyfile,args = (photoPath['InputOriginal'],photoPath['Output']))
		# 	p.start()
		# else:
		# 	p = Process(target = pilSaveHelper,args = (imageRotated,photoPath['Output']))
		# 	p.start()
		returnOrientation.append({'InputOriginal':photoPath['InputOriginal'],'Output':photoPath['Output'],'Orientation':photoOrientation})
		# os.remove(photoPath['Input'])
		#save in two places, remove input
	# elif photoOrientation == 'D': #delete photo
	# 	shutil.copyfile(photoPath['InputThumb'],photoPath['Processed'])
		# os.remove(photoPath['Input'])
	elif photoOrientation == 'z' and photoPath['photoPathIO_prev']:
		returnOrientation += handleImage(photoPath['photoPathIO_prev'])
		returnOrientation += handleImage(photoPath) #this photoPath must be redone because the command was 'z'

	RotationLog.appendRotationLog([photoPath['InputOriginal']])

	# print 'rotationOrientation: {0}'.format(returnOrientation)

	return returnOrientation

def rotateImageSave(imagePackage):
	# for imagePackage in imagePackages:
		# print 'imagePackage: {0}'.format(imagePackage)
		# raw_input('save, ok?')
		if imagePackage['Orientation'] == '0':
			shutil.copy(imagePackage['InputOriginal'],imagePackage['Output'])
		else:
			img = Image.open(imagePackage['InputOriginal']).rotate(int(imagePackage['Orientation']) * 90,expand=True)
			img.save(imagePackage['Output'],'JPEG',quality = 100)
		# RotationLog.appendRotationLog([imagePackage['InputOriginal']])

def manualRotate(photoPathsInput):
	# photoPathsInput = []
	# for root, dirs, files in os.walk(baseInputPath.replace('SCANS','SCANS_RotThumb')):
	# 	for name in files:
	# 		photoPathsInput.append(os.path.join(root,name))
	# print 'photoPathsInput: {0}'.format(photoPathsInput)
	

	photoPathsOutput = []
	photoPathsOriginal = []
	for path in photoPathsInput:
		#not robust, but very easy to implement
		#fails if there are sub-folders with the same name as a parent
		photoPathsOriginal.append(path.replace('SCANS_RotThumb','SCANS'))
		photoPathsOutput.append(path.replace('SCANS_RotThumb','SCANS_Rotated'))

	photoPathsZip = zip(photoPathsInput,photoPathsOriginal,photoPathsOutput)
	photoPathsIO = [{'InputThumb':ith,'InputOriginal':ior,'Output':o} for (ith,ior,o) in photoPathsZip if ith.split('/')[-1][0] != '.']
	
	if photoPathsIO != []:
		photoPathsIO[0]['photoPathIO_prev'] = {}
		for index in range(len(photoPathsIO)-1):
			photoPathsIO[index+1]['photoPathIO_prev'] = photoPathsIO[index]

		procs = []
		orientation = []
		for count,photoPath in enumerate(photoPathsIO):
			orientation += handleImage(photoPath)
			if count % 4 == 3:
				for orient in orientation:
					p = Process(target = map,args = (rotateImageSave,(orient,)))
					p.start()
					procs.append(p)
				orientation = []

		for orient in orientation:
					p = Process(target = map,args = (rotateImageSave,(orient,)))
					p.start()
					procs.append(p)

		# rotateImageSave(orientation)

		# procs = []
		# numProcs = 4
		# step = len(orientation)/numProcs +1
		# for index in range(numProcs):
		# 	p = Process(target = map,args = (rotateImageSave,orientation[index*step:index*step+step]))
		# 	p.start()
		# 	procs.append(p)

		for p in procs:
			p.join()
		# raw_input('you good?')


if __name__ == "__main__":
	### finally perform any needed manual rotation
	if len(sys.argv) > 1:
		# print '###input args: {0}'.format(sys.argv[1:])
		baseInputPath = sys.argv[1]
		baseInputPath = baseInputPath[:baseInputPath.index('SCANS') + len('SCANS')]
		baseRotatedPath = baseInputPath + '_Rotated'
		filesRotated = RotationLog.getRotationLog(baseRotatedPath)
		filesUnrotated = RotationLog.checkUnrotatedFile(filesRotated,sys.argv[1:])
		filesUnrotated = [f.replace('SCANS/','SCANS_RotThumb/') for f in filesUnrotated]

		# print '###filesUnrotated: {0}'.format(filesUnrotated)
		manualRotate(filesUnrotated)