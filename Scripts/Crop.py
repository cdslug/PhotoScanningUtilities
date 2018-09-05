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
import math

#DEBUG = True

def highlightBlack(img, thresholdBlack):
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if np.average(img[x,y,:]) < thresholdBlack:
                img[x,y,2] += 50
                img[x,y,1] += 50
                img[x,y,0] += 50
    return img

def detectBorders(img):
    borders = { "yMax":0,
                "yMin":0,
                "xMax":0,
                "xMin":0
                }
    w,h,_ = img.shape
    thresholdBlack = 100 #10 is just a quick trial and error
    # #print("image depth = {}".format(img.depth()))
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

    #print(borders)
    return borders

def naiveBounds(imgRGB, colorThreshold,offsetRatio=0):
    #look at the middle rows and columns
    #find first acceptable pixels for a rough boundary
    #print("imgRGB shape: {}".format(imgRGB.shape))
    img = np.ndarray.max(imgRGB,axis=2)
    h,w = img.shape
    top = int(np.argmax(img[:,h/2] > colorThreshold) + offsetRatio*h) #add slight angle colorThresholderance
    bottom = int(h - (np.argmax(img[::-1,h/2] > colorThreshold) + offsetRatio*h))
    left = int(np.argmax(img[w/2,:] > colorThreshold) + offsetRatio*w)
    right = int(w - (np.argmax(img[w/2,::-1] > colorThreshold) + offsetRatio*w))
    #print("top: {}, bottom {}, left {}, right {}".format(top,bottom,left,right))
    return (top, bottom, left, right)

def findBounds(imgRGB,colorThreshold):
    img = np.ndarray.max(imgRGB,axis=2)
    h,w = img.shape
    offsetRatio = 0.05
    top,bottom,left,right = naiveBounds(imgRGB,colorThreshold,offsetRatio)
    # print("top: {}, bottom: {}, left: {}, right: {}".format(top,bottom,left,right))
    def spreadDimPoints(dimLen,minDetected,maxDetected):
        divisions = 10 #needs to be even if it want it balanced
        offset = (maxDetected - minDetected)/(divisions-1)
        singleDimPoints = []
        for index in range(divisions):
            d = minDetected + index * offset #-1 because I want the right boundary included
            d = int(d)
            singleDimPoints.append(d)
        return singleDimPoints

    boundsDetected = {"BoundsTop":[],
                      "BoundsBottom":[],
                      "BoundsLeft":[],
                      "BoundsRight":[]
                     }

    xPoints = spreadDimPoints(w,left,right)
    #points on top
    for x in xPoints:
        y = np.argmax(img[:,x] > colorThreshold)
        # print(y)
        if y < h:
            boundsDetected["BoundsTop"].append([x,y])
    #points on bottom
    for x in xPoints:
        y = np.argmax(img[::-1,x] > colorThreshold)
        y = h-y
        if 0 < y:
            boundsDetected["BoundsBottom"].append([x,y])

    #print("h: {}, top: {}, bottom: {}".format(h, top, bottom))
    yPoints = spreadDimPoints(h,top,bottom)
    #points on left
    for y in yPoints:
        x = np.argmax(img[y,:] > colorThreshold)
        if 0 < x:
            boundsDetected["BoundsLeft"].append([x,y])
    #points on right
    for y in yPoints:
        x = np.argmax(img[y,::-1] > colorThreshold)
        x = w - x
        if x < w:
            boundsDetected["BoundsRight"].append([x,y])

        try:
            DEBUG
        except NameError:
            pass
        else:
            for key in boundsDetected.keys():
                #set points for finding slopes of boundary
                points = boundsDetected[key]
                #TESTING: show points while testing
                for p in points:
                    # print(p)
                    img[p[1],p[0]] = 255
                    #img[p[1]-2:p[1]+2,p[0]-2:p[0]+2] = 255
                    # img[p[3]-2:p[3]+2,p[2]-2:p[2]+2] = 255
    return boundsDetected

def rotate_image2(img, colorThreshold=0):
    h,w,_ = img.shape

    offsetRatio = 0.05

    firstLeft = 0
    img_mask = img > colorThreshold

    for index in range(w):
        if np.max(img[:,index]) == 1:
            firstLeft = index
            break

    firstRight = 0
    for index in reversed(range(w)):
        if np.max(img[:,index]) == 1:
            firstRight = index
            break




def rotate_image(img, colorThreshold=0):
    h,w,_ = img.shape

    offsetRatio = 0.05
    top,bottom,left,right = naiveBounds(img,colorThreshold,offsetRatio)
    # print("top: {}, bottom: {}, left: {}, right: {}".format(top,bottom,left,right))

    #points on top and bottom

    boundsDetected = findBounds(img,colorThreshold)

    # print("### boundsDetected: {}".format(boundsDetected))
    pointList = [] #[x1,y1,x2,y2]
    for key in boundsDetected.keys():
        #set points for finding slopes of boundary
        points = boundsDetected[key]
        indexOffset = len(points)/2
        for index in range(indexOffset):
            pointList.append([points[index][0],points[index][1],
                              points[index + indexOffset][0],points[index + indexOffset][1]
                              ])

    #print("pointList {}\n".format(pointList))

    #calculate slopes
    slopes = []
    for pl in pointList:
        # print("pl: {}".format(pl))
        numerator = float(pl[3] - pl[1])
        denomenator = float(pl[2]-pl[0])

        #flip for left right bounds
        if abs(numerator) > abs(denomenator):
            numerator,denomenator = (-denomenator,numerator)

        if denomenator == 0:
            slopes.append(float("inf"))
        else:
            slope = numerator/denomenator
            slopes.append(slope)
    # print("slopes {}\n".format(slopes))

    meanSlope = np.mean(slopes)
    #print("mean slope : {}\n".format(meanSlope))

    stdSlope = np.std(slopes)
    #print("std slope: {}\n".format(stdSlope))

    #filter outlier slopes
    slopes = list(filter(lambda x: abs(meanSlope-x) < abs(stdSlope),slopes))

    meanSlope = np.mean(slopes)
    #print("mean slope fixed : {}\n".format(meanSlope))

    absSlopes = [abs(s) for s in slopes]
    #print("abs(slopes): {}\n".format(absSlopes))

    minSlopeIndex = np.argmin([abs(s) for s in slopes])
    minSlope = slopes[minSlopeIndex]
    #print("min slope: {}\n".format(meanSlope))

    degrees = math.degrees(math.atan(meanSlope))
    #print("degrees: {}\n".format(degrees))

    M = cv2.getRotationMatrix2D((w/2,h/2),degrees,1)
    img = cv2.warpAffine(img,M,(w,h))

    return img

def removeOutliers(dimList):
    dimMean = np.mean(dimList)
    dimSTD = np.std(dimList)
    filteredDimList = list(filter(lambda x: abs(dimMean-x) <= abs(dimSTD),dimList))
    return filteredDimList

def singleSTDThresold(data):
    mu = np.mean(data)
    sigma = np.std(data)
    data = list(filter(lambda x: abs(x-mu) < sigma, data))
    return data

def findCropBounds(img,colorThreshold=0, acceptedRatios = [1.5,0.66,1]):
    h,w,_ = img.shape

    boundsFound = findBounds(img,colorThreshold)

    points = boundsFound["BoundsTop"]
    tops = [y for x,y in points]
    # tops = removeOutliers(tops)]
    top = singleSTDThresold(tops)
    top = int(min(tops))
    #print("tops: {}".format(tops))

    points = boundsFound["BoundsBottom"]
    bottoms = [y for x,y in points]
    # bottoms = removeOutliers(bottoms)
    bottoms = singleSTDThresold(bottoms)
    bottom = int(max(bottoms))

    points = boundsFound["BoundsLeft"]
    lefts = [x for x,y in points]
    # lefts = removeOutliers(lefts)
    lefts = singleSTDThresold(lefts)
    left = int(min(lefts))

    points = boundsFound["BoundsRight"]
    rights = [x for x,y in points]
    # rights = removeOutliers(rights)
    rights = singleSTDThresold(rights)
    right = int(max(rights))

    #print("top: {}, bottom: {}, left: {}, right: {}".format(top,bottom,left,right))

    try:
        DEBUG
    except NameError:
        pass
    else:
        cv2.rectangle(img,(left,top),(right,bottom),(200,200,200))

    #verify the ratio
    acceptableRatio = False
    ratio = float(bottom-top)/float(right-left)
    #print("ratio: {}\n".format(ratio))
    for ir in acceptedRatios:
        # print("{:.4f} vs {:.4f}".format(abs(ir-ratio)*100,ir * 0.015))
        if abs(ir-ratio) < ir * 0.015:
            acceptableRatio = True
            break
    else:
        top,bottom,left,right = [0,h,0,w]
        acceptableRatio = False

    return [(top,bottom,left,right),acceptableRatio]

def crop_image(img,
               colorThreshold=0,
               acceptedRatios = [1.5,0.66,1],
               additionalCropRatio = 0.05):

    h,w,_ = img.shape

    [top,bottom,left,right],checkCropped = findCropBounds(img,colorThreshold,acceptedRatios)

    if checkCropped == True:
        top = top + int((h * additionalCropRatio))
        bottom = bottom - int((h * additionalCropRatio))
        left = left + int((w * additionalCropRatio))
        right = right - int((w * additionalCropRatio))
    try:
        DEBUG
    except NameError:
        pass
    else:
        #print("top: {}, bottom: {}, left: {}, right: {}".format(top,bottom,left,right))
        cv2.rectangle(img,(left,top),(right,bottom),(255,255,255))
        #print(img.shape)
        return img,checkCropped

    return img[top:bottom,left:right,:],checkCropped

def main():
    timeStart = time.time()
    imagePath = sys.argv[1]

    img = cv2.imread(imagePath)
    thumbScale = 0.10
    wThumb = int(img.shape[1]*thumbScale)
    hThumb = int(img.shape[0]*thumbScale)
    img = cv2.resize(img,(wThumb,hThumb)) #speed up for testing

    average = np.average(img[0:25,0:25,:],axis=(0,1))
    #print("Average Pixel Value R:{},G:{},B:{}".format(average[0],average[1],average[2]))



    colorThreshold = 20
    img = rotate_image(img,colorThreshold)
    acceptedRatios = [1.5,0.66,1]
    additionalCropRatio = 0.005
    img,checkCropped = crop_image(img,
                                  colorThreshold,
                                  acceptedRatios,
                                  additionalCropRatio)
    timeStop = time.time()
    # img = highlightBlack(img,colorThreshold)

    #print("### time taken = {}".format(timeStop-timeStart)) #2.33s
    cv2.imshow("cropped?: {}".format(checkCropped), img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
