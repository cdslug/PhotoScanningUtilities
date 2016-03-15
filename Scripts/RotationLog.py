import os

def getRotationLog(baseRotatedPath):
	rotatedPics = []
	for root, directories,files in os.walk(baseRotatedPath):
		for name in files:
			rotatedPics.append(name)
	return rotatedPics

def checkUnrotatedFiles(rotatedPics,inputPaths):
	filePathsInput = []
	for f in inputPaths:
		if os.path.isfile(f) and f.split('/')[-1] not in rotatedPics:
			filePathsInput.append(f)
		else:
			for root, dirs, files in os.walk(f):
				#root must always have 'Scans' at the end
				for name in files:
					if name not in rotatedPics:
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