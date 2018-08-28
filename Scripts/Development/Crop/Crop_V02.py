import os
import sys
import termios
import shutil
from PIL import Image, ImageTk
import cv2
import Tkinter as tk
import multiprocessing
import numpy as np
import time

def highlightBlack(img):
    thresholdBlack = 10 #10 is just a quick trial and error
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if np.average(img[x,y,:]) < thresholdBlack:
                img[x,y,2] = 255
                img[x,y,1] = 0
                img[x,y,0] = 0
    return img

def detectBorders(img):
    borders = { "yMax":0,
                "yMin":0,
                "xMax":0,
                "xMin":0
                }
    w,h,_ = img.shape
    thresholdBlack = 100 #10 is just a quick trial and error
    # print("image depth = {}".format(img.depth()))
    for index in range(h):
        if np.average(img[::4,h-1-index,:]) > thresholdBlack:
            borders["yMax"] = h-1-index
    for index in range(h):
        if np.average(img[::4,index,:]) > thresholdBlack:
            borders["yMin"] = index
    for index in range(w):
        if np.average(img[w-1-index,::4,:]) > thresholdBlack:
            borders["xMax"] = w-1-index
    for index in range(w):
        if np.average(img[index,::4,:]) > thresholdBlack:
            borders["xMin"] = index

    print(borders)
    return borders

def crop_image(img,tol=0):
    # img is image data
    # tol  is tolerance
    img = img[:,:,0]
    mask = img>tol #red
    return img[np.ix_(mask.any(1),mask.any(0))]

timeStart = time.time()
imagePath = sys.argv[1]

img = cv2.imread(imagePath)
thumbScale = 0.10
wThumb = int(img.shape[1]*thumbScale)
hThumb = int(img.shape[0]*thumbScale)
img = cv2.resize(img,(wThumb,hThumb)) #speed up for testing

average = np.average(img[0:25,0:25,:],axis=(0,1))
print("Average Pixel Value R:{},G:{},B:{}".format(average[0],average[1],average[2]))

img = highlightBlack(img)


img = crop_image(img,100)
timeStop = time.time()
print("### time taken = {}".format(timeStop-timeStart)) #2.33s
cv2.imshow("cropped", img)
cv2.waitKey(0)
