import os
import sys
import termios
import shutil
from PIL import Image, ImageTk
import cv2
import Tkinter as tk
import multiprocessing

class keycode:
	KEY_ESCAPE = 27
	###The ESC key

	KEY_DOWN = 63233
	###The Arrow Down key

	KEY_LEFT = 63234
	###The Arrow Left key

	KEY_RIGHT = 63235
	###The Arrow Right key

	###keycode.KEY_SPACE = 32
	###The Space key

	KEY_UP = 63232
	###The Arrow Up key

	KEY_q = ord('q')
	KEY_d = ord('d')
	KEY_z = ord('z')
	keys = [KEY_ESCAPE,KEY_UP,KEY_RIGHT,KEY_DOWN,KEY_LEFT,KEY_q,KEY_d,KEY_z]

def askPhotoOrientation(imagePath):
	smallSize = 500

	if imagePath == None:
		return '0'
		
	imgCV2 = cv2.imread(imagePath)
	print 'Image Path: {0}'.format(imagePath)
	scaleRatio = smallSize/float(max(imgCV2.shape[:-1]))
	# print 'Scale Ratio: {0}'.format(scaleRatio)
	imgCV2Thumb = cv2.resize(imgCV2, (0,0), fx=scaleRatio,fy=scaleRatio)

	# windowName = imagePath.split('/')[-1]
	windowName = 'img'
	cv2.imshow(windowName,imgCV2Thumb)	

	userInput = ''
	rotationDirection = ''
	acceptedCommands = keycode.keys
	while rotationDirection == '':
		#don't alow accidental repeated entries
		termios.tcflush(sys.stdin,termios.TCIOFLUSH)
		# rotationDirection = raw_input('Type Rotation Angle (0,1,2,3) *90\t')
		userInput = cv2.waitKey(0)
		if userInput not in keycode.keys:
			print 'input not accepted'
			continue
		#handle issues
		if userInput == keycode.KEY_d:
			# rotationDirection = raw_input('Really delete? Type \'d\' to confirm, otherwise enter a rotation angle.')
			userInput = cv2.waitKey(0)
			if userInput == keycode.KEY_d:
				rotationDirection = 'd'
		elif userInput == keycode.KEY_UP:
			rotationDirection = '0'
		elif userInput == keycode.KEY_RIGHT:
			rotationDirection = '1'
		elif userInput == keycode.KEY_DOWN:
			rotationDirection = '2'
		elif userInput == keycode.KEY_LEFT:
			rotationDirection = '3'
		elif userInput in [keycode.KEY_q,keycode.KEY_ESCAPE]:
			cv2.destroyAllWindows()
			sys.exit('Following User\'s Orders, Exiting Rotation Script.')
		elif userInput == keycode.KEY_z:
			rotationDirection = 'z'
	cv2.destroyWindow(windowName)
	return rotationDirection

def handleImage(photoPath, photoPathOld):
	photoOrientation = askPhotoOrientation(photoPath['Input'])

	if photoOrientation.isdigit():
		imageRotated = Image.open(photoPath['Input']).rotate(int(photoOrientation) * 90,expand=True)
		# shutil.copyfile(photoPath['Input'],photoPath['Processed'])
		if photoOrientation == '0':
			shutil.copyfile(photoPath['Input'],photoPath['Output'])
		else:
			imageRotated.save(photoPath['Output'],'JPEG',quality = 100)
		# os.remove(photoPath['Input'])
		#save in two places, remove input
	elif photoOrientation == 'd': #delete photo
		shutil.copyfile(photoPath['Input'],photoPath['Processed'])
		# os.remove(photoPath['Input'])
	elif photoOrientation == 'z' and photoPathOld != {}:
		handleImage(photoPathOld,{})
		handleImage(photoPath, photoPathOld)


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

			for photoPath in photoPathList:
				fileFormats = ['.jpg','.png']
				# print photoPath
				print photoPath['Input'].split('/')[-1]
				if photoPath['Input'].split('/')[-1][0] != '.' and photoPath['Input'][-4:] in fileFormats:

					handleImage(photoPath,photoPathOld)
				#this seems messy not to include it with the code that copies pictures
				#remove the input photo since it is no longer in the safety undo variable
				# if photoPathOld != {}:
					# os.remove(photoPathOld['Input'])
				photoPathOld = photoPath

			# os.remove(photoPathOld['Input'])
			#cleanup if empty
			print 'In the end, album has: ' + str(os.listdir(albumPath['Input']))
			# if len(set(os.listdir(albumPath['Input'])) - set(['.DS_Store'])) == 0:
			# 	shutil.rmtree(albumPath['Input'])
					
					
########################
#####     MAIN     #####
########################
### Steps
### in each directory and each file
###	display a preview of the photo
###	use input responses to rotate the photo
### safe the photo
if __name__ == '__main__':
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
