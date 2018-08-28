import RotationLog
import Rotate_Auto
import Rotate_Manual

import sys
import os

def countFiles(path):
	fileCount = 0

	if os.path.isfile(path):
		fileCount += 1
	else:
		for root, dirs,files in os.walk(path):
			fileCount += len([f for f in files if f[-4:].lower() in ['.jpg','.JPG','.png']])

	return fileCount

def subFiles(inputPaths):
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

if __name__ == '__main__':
	inputFilePaths = subFiles(sys.argv[1:])
	baseInputPath = sys.argv[1]
	baseInputPath = baseInputPath[:baseInputPath.index('SCANS') + len('SCANS')]
	statsFile = os.path.join(baseInputPath,'RotationStats.csv')
	if not os.path.isfile(statsFile):
		with open(statsFile,'w') as sf:
			sf.write('AutoRotated,ManualRotated,TotalRotated\n')

	baseRotatedPath = baseInputPath + '_Rotated'

	initialRotatedCount = countFiles(baseRotatedPath)
	#depends on the behavior that hidden files starting with '.' are not copied over to other folders
	filesRotated = RotationLog.getRotationLog(baseRotatedPath)
	filesUnrotated = RotationLog.checkUnrotatedFiles(filesRotated,inputFilePaths)
	filesUnrotated.sort()
	for fU in filesUnrotated:
		try:
			tempIndex = fU.index('SCANS')
			print(fU)
		except ValueError:
			print('### {}'.format(fU))
	Rotate_Auto.rotatePipelined(filesUnrotated)

	autoRotatedCount = countFiles(baseRotatedPath) - initialRotatedCount
	###Rotate Manual at end so files to be rotated are the same

	filesRotated = RotationLog.getRotationLog(baseRotatedPath)
	filesUnrotated = RotationLog.checkUnrotatedFiles(filesRotated,inputFilePaths)
	filesUnrotated.sort()

	filesUnrotated = [f.replace('SCANS/','SCANS_RotThumb/') for f in filesUnrotated]

	# 	# print '###filesUnrotated: {0}'.format(filesUnrotated)
	### TODO: needs to handle the case when there are no thumbnails in the thumbnail folder
	Rotate_Manual.manualRotate(filesUnrotated)

	totalRotatedCount = countFiles(baseRotatedPath) - initialRotatedCount
	manualRotatedCount = totalRotatedCount - autoRotatedCount

	with open(statsFile,'a') as sf:
		sf.write('{0},{1},{2}\n'.format(autoRotatedCount,manualRotatedCount,totalRotatedCount))
