import os
import sys
import numpy as np
import cv2 
from PIL import Image
import numpy

def detect(path):
	print 'Searching {}'.format(path)

	upCascade = cv2.CascadeClassifier('/Users/cdslug/Downloads/opencv-master/data/haarcascades/haarcascade_frontalface_default.xml')


	imagePIL = Image.open(path).convert('RGB')
	if max(imagePIL.size) > 300:
		imagePIL.thumbnail((300,300), Image.ANTIALIAS)
	size = imagePIL.size
	width,height = size
	dim = max(size)
	sqImagePIL = Image.new('RGB',(dim,dim))

	# sqImagePIL.paste(imagePIL,(0,0))
	sqImagePIL.paste(imagePIL,(dim/2-width/2,dim/2-height/2))

	img = numpy.array(sqImagePIL)
	img = img[:,:,::-1].copy()
	print img.shape
	rows,cols,dummy = img.shape

	M = cv2.getRotationMatrix2D((cols/2,rows/2),-90,1)
	img = cv2.warpAffine(img,M,(cols,rows))
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	ups = upCascade.detectMultiScale(gray, 1.3, 5)
	# (x,y,w,h) = (20,20,20,20)
	# cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
	for (x,y,w,h) in ups:
		# (x,y,w,h) = (20,20,20,20)
		cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

	cv2.imshow('img',img)
	if cv2.waitKey(0) == ord('q'):
		sys.exit()
	# if 'q' == raw_input('type something'):
	# 	cv2.destroyAllWindows()
	# 	sys.exit()

	cv2.destroyAllWindows()

def albumRecursion(path):
	

	if os.path.isdir(path):
		for p in [os.path.join(path,f) for f in os.listdir(path)]:
			albumRecursion(p)
	elif path[-4:] in ['.png','.jpg'] and path[0] != '.':
		detect(path)

albumRecursion(sys.argv[1])