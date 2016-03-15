import os
import sys
import termios
import shutil
from PIL import Image, ImageTk
import Tkinter as tk
import multiprocessing
import time


def askPhotoOrientation(imagePath,stdin):
	root = tk.Tk()
	root.title(imagePath.split('/')[-1])
	smallSize = 500,500
	imagePIL = Image.open(imagePath)
	imagePIL.thumbnail(smallSize, Image.ANTIALIAS)
	image1 = ImageTk.PhotoImage(imagePIL)

	w = image1.width()
	h = image1.height()
	screenWidth = root.winfo_screenwidth()
	screenHeight = root.winfo_screenheight()
	x = (screenWidth/2)-(w/2)
	y = (screenHeight/2)-(h/2)

	root.geometry('%dx%d+%d+%d' % (w,h,x,y))

	panel1 = tk.Label(root, image=image1)
	panel1.pack(side='top',fill='both',expand='yes')
	panel1.image = image1

	# root.mainloop()
	rotationDirection = ''
	acceptedCommands = ['0','1','2','3','D']
	while rotationDirection not in acceptedCommands:
		#don't alow accidental repeated entries
		termios.tcflush(sys.stdin,termios.TCIOFLUSH)
		# rotationDirection = raw_input('Type Rotation Angle (0,1,2,3) *90\t')
		rotationDirection = stdin.readline('Type Rotation Angle (0,1,2,3) *90\t')
		#####     TESTING ONLY     #####
		# rotationDirection = '2'

		#handle issues
		if rotationDirection == 'D':
			rotationDirection = raw_input('Really delete? Type \'D\' to confirm, otherwise enter a rotation angle.')
		elif rotationDirection.isdigit() and 3 < int(rotationDirection) < 0:
			rotationDirection = raw_input('angle must be an integer coefficient of 90 within 360: 0,1,2,3')
		if rotationDirection == 'q':
			sys.exit('Following User\'s Orders, Exiting Rotation Script.')
	root.destroy()
	return rotationDirection

def handleImage(photoPath, stdin):
	photoOrientation = askPhotoOrientation(photoPath['Input'], stdin)

	if photoOrientation.isdigit():
		imageRotated = Image.open(photoPath['Input']).rotate(int(photoOrientation) * 90,expand=True)
		shutil.copyfile(photoPath['Input'],photoPath['Processed'])
		if photoOrientation == '0':
			shutil.copyfile(photoPath['Input'],photoPath['Output'])
		else:
			imageRotated.save(photoPath['Output'],'JPEG',quality = 100)
		os.remove(photoPath['Input'])
		#save in two places, remove input
	elif photoOrientation == 'D': #delete photo
		shutil.copyfile(photoPath['Input'],photoPath['Processed'])
		os.remove(photoPath['Input'])
	# elif photoOrientation == 'z' and photoPathOld != {}:
	# 	handleImage(photoPathOld,{})
	# 	handleImage(photoPath, photoPathOld)


def removePhoto_Worker(photoFile):
	os.remove(photoFile)
	print 'photo removed in side process'
	return

def rotatePhotos(inputPath, processedPath, outputPath):
	albumPathList = [{	'Input':os.path.join(inputPath, a),
						'Processed':os.path.join(processedPath, a),
						'Output':os.path.join(outputPath, a)
					 } 
						for a in os.listdir(inputPath)]

	for albumPath in albumPathList:
		print albumPath['Input']
		# print os.path.isdir(albumPath['Input'])
		if os.path.isdir(albumPath['Input']):
			if not os.path.exists(albumPath['Processed']):
				os.makedirs(albumPath['Processed'])
			if not os.path.exists(albumPath['Output']):
				os.makedirs(albumPath['Output'])

			photoPathList = [{	'Input':os.path.join(albumPath['Input'],p),
								'Processed':os.path.join(albumPath['Processed'],p),
								'Output':os.path.join(albumPath['Output'],p)
							 }
								 for p in os.listdir(albumPath['Input'])]
			#allow undoing a mistake, except for last photo
			photoPathOld = {}
			taskList = []

			newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
			for photoPath in photoPathList:
				# print photoPath
				print photoPath['Input'].split('/')[-1]
				if photoPath['Input'].split('/')[-1][0] != '.' and photoPath['Input'][-4:] == '.jpg':
					newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
					p = multiprocessing.Process(target=handleImage,args=(photoPath,newstdin,))
					taskList.append(p)
					p.start()
					time.sleep(1)
					p.join()
					newstdin.close()
					# handleImage(photoPath,photoPathOld)
				#this seems messy not to include it with the code that copies pictures
				#remove the input photo since it is no longer in the safety undo variable
				# if photoPathOld != {}:
				# 	taskList.append(multiprocessing.Process(target = removePhoto_Worker,args = (photoPathOld['Input'],)))
				# photoPathOld = photoPath

			# os.remove(photoPathOld['Input'])
			#cleanup if empty
			print 'In the end, album has: ' + str(os.listdir(albumPath['Input']))
			if len(set(os.listdir(albumPath['Input'])) - set(['.DS_Store'])) == 0:
				shutil.rmtree(albumPath['Input'])
					
					
########################
#####     MAIN     #####
########################
### Steps
### in each directory and each file
###	display a preview of the photo
###	use input responses to rotate the photo
### safe the photo
inputPath = sys.argv[1]
outputPath = sys.argv[2]

#make sure input paths already exist
if not os.path.exists(inputPath):
		sys.exit('Error: ' + inputPath + ' does not exist')
if not os.path.exists(outputPath):
		sys.exit('Error: ' + outputPath + ' does not exist')

#create directory to transfer photos that have already been processed
processedPath = inputPath + '_Processed'
if not os.path.exists(processedPath):
	os.makedirs(processedPath)

rotatePhotos(inputPath, processedPath, outputPath)
