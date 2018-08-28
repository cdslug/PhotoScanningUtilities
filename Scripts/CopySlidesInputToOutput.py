import os
import sys
import getch
import shutil


scanningDir = sys.argv[1]

newScansDir = os.path.join(scanningDir, "NEWFOLDER")
if not os.path.isdir(newScansDir):
    os.mkdir(newScansDir)

outputDir = os.path.join(scanningDir,"Untitled")

print("Press <Space> to copy files from 'NEWFOLDER' to 'Untitled/#'")
while True:
    readch = getch.getche()
    if readch == " ":
        ###Folter is finished, create new folder
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)
        dirList = []
        for root, dirs, files in os.walk(outputDir):
            #assumes dirs are numbers
            for d in dirs:
                if len(d) > 0:
                    dirList.append(int(d))
        nextDir = 1
        if len(dirList) > 0:
            dirList.sort()
            nextDir = dirList[-1] + 1
        ###assume the file hasn't been created after this previous os.walk()
        nextDirPath = os.path.join(outputDir,str(nextDir))
        os.mkdir(nextDirPath)

        ###copy the files from the temp
        for root, dirs, files in os.walk(newScansDir):
            for f in files:
                shutil.move(os.path.join(root,f),nextDirPath)
        print("Moved to {:02}".format(nextDir))
    elif readch == "\n":
        ###batch is finished, rename the input folder to "UNTITLED"
        pass
    else:
        exit()
