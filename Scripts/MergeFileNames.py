import os
import sys
import shutil

inputPaths = sys.argv[1:-1]
outputPaths = sys.argv[-1]

inputFiles = []
for p in inputPaths:
	inputFiles.expand(os.listdir(p))

inputFiles.sort(key=lambda x:x.split('/')[-1])

fileCounter = 1

for ip in inputPaths:
	shutil.copy(ip,'{0}/IMG_{1:04d}'.format(outputPath,fileCounter))
	fileCounter += 1