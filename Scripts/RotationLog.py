import os

def getRotationLog(baseRotatedPath):
	rotatedPics = []
	for root, directories,files in os.walk(baseRotatedPath):
		for name in files:
			print("### getRotationLog: name = ".format(name))
			if name[-4:] in ['.jpg','.JPG','.png','.PNG']:
				rotatedPics.append(os.path.join(root,name))
	return rotatedPics

def checkUnrotatedFiles(rotatedPicsOriginal,inputPaths):
	filePathsInput = []

	inputSCANSIndex = None
	print("### checkUnrotatedFiles: len(rotatedPicsOriginal) {}".format(len(rotatedPicsOriginal)))

	for index,rp in enumerate(inputPaths[0].split('/')):
		if 'SCANS' in rp:
			inputSCANSIndex = index + 1
			break

	rotatedSCANSIndex = None
	if len(rotatedPicsOriginal) > 0:
		for index,rp in enumerate(rotatedPicsOriginal[0].split('/')):
			if 'SCANS' in rp:
				rotatedSCANSIndex = index + 1
				break

	rotatedPics = [''.join(f.split('/')[rotatedSCANSIndex:]) for f in rotatedPicsOriginal]

	for f in inputPaths:
		inputSubPath = ''.join(f.split('/')[inputSCANSIndex:])

		if os.path.isfile(f) and inputSubPath not in rotatedPics:
			if f[-4:] in ['.jpg','.JPG','.png','.PNG']:
				filePathsInput.append(f)
		else:
			for root, dirs, files in os.walk(f):
				#root must always have 'Scans' at the end
				for name in files:
					if name not in rotatedPics:
						if name[-4:] in ['.jpg','.JPG','.png','.PNG']:
							filePathsInput.append(os.path.join(root,name))
						# print name
	return filePathsInput

### inputPaths must be a list
def getAllUnrotatedFiles(rotatedPics,inputPaths):
	filePathsInput = []
	for f in inputPaths:
		if os.path.isfile(f) and f.split('/')[-1]  not in rotatedPics:
			filePathsInput.append(f)
		# f = f[:f.index('SCANS') + len('SCANS')]
		elif os.path.isdir(f):
			for root, dirs, files in os.walk(f):
				#root must always have 'Scans' at the end

				for name in files:
					if name not in rotatedPics:
						filePathsInput.append(os.path.join(root,name))
					# print name
	return filePathsInput

def appendRotationLog(filePaths):
	if len(filePaths) != 0:
		logFilePath = filePaths[0][:filePaths[0].index('SCANS') + len('SCANS')] + '/.RotationLog.txt'
		open(logFilePath, 'a').close()
		with open(logFilePath,'a') as f:
			for name in [fp.split('/')[-1] for fp in filePaths]:
				f.write(name + '\n')
