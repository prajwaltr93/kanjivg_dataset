#filename : create_globaldataset.py
#author : PRAJWAL T R
#date last modified : Mon Jul  13 11:09:55 2020
#comments :

'''
    simple module with some basic drawing functions and user defined datatypes ex : class Point
'''

import cv2 as cv
import re
import matplotlib.pyplot as plt
import numpy as np
from bresenhamsalgo import getPoints

# globals
WIDTH = 100
HEIGHT = 100
COLOR = 1
crop_img_size = 5
THICKNESS = 1
LINE_TYPE = cv.LINE_AA
path_re = re.compile(r'\t(.*)\n')
points_re = re.compile(r'(\d+),\s(\d+)')
test_dir_path = "./test_dir/"
TEST = 2
TRAIN = 0
VALIDATION = 1

#debug functions
def showImage(img):
    cv.imshow("show window",img)
    cv.imwrite("debug_image_out.png",img)
    cv.waitKey(0)

# drawing utility functions
def parsePointString(point_string):
    #get x and y cordinate out of point_string
    result_points = points_re.search(point_string)
    return (int(result_points.group(1)), int(result_points.group(2)))

def drawPoint(point):
    '''
        point : list of x,y
        if point == Nan:
            generate empty image
        else:
            mark point in white color ex : for argmax
            background in black
        returns numpy representation of images
    '''
    img = np.zeros((HEIGHT,WIDTH))
    if point.x == 0 and point.y == 0:
        #generate black background image
        return img
    else:
        #mark white dot
        img[point.y][point.x] = COLOR
    return img

def drawStroke(strokes):
    '''
        stroke
            ex :
                M 34,45
                L 32,32
                L 14,14
        parse stroke and generate corresponding image

        if stroke == None
            generate empty image
        returns numpy representation of images
    '''
    img = np.zeros((HEIGHT,WIDTH))
    if len(strokes) == 0:
        #generate empty image
        return img
    #X_last X_env X_diff
    m_indices = []
    for search_ind, path in zip(range(len(strokes)), strokes.__iter__()):
        if path[0] == 'M':
            m_indices.append(search_ind)
    for ind in range(len(m_indices) - 1):
        slice = strokes[m_indices[ind] : m_indices[ind + 1]]
        for ind in range(len(slice) - 1):
            cv.line(img, parsePointString(slice[ind]), parsePointString(slice[ind+1]),COLOR,THICKNESS,LINE_TYPE)
    #for length of m_indices = 1 and drawing end strokes
    slice = strokes[m_indices[-1] : ]
    for ind in range(len(slice) - 1):
        cv.line(img, parsePointString(slice[ind]), parsePointString(slice[ind+1]),COLOR,THICKNESS,LINE_TYPE)
    return img

def getStrokesIndices(svg_string):
    #get path string
    X_target = path_re.findall(svg_string)
    m_indices = []
    for search_ind, path in zip(range(len(X_target)),X_target.__iter__()):
        if path[0] == 'M':
            m_indices.append(search_ind)
    return X_target, m_indices

def drawFromPoints(points):
    #if points = empty then return blank image

    img = np.zeros((HEIGHT, WIDTH))

    if len(points) == 0:
        return img

    #else draw for each point
    for ind in range(len(points) - 1):
        cv.line(img, points[ind], points[ind + 1],COLOR, THICKNESS, LINE_TYPE)
    return img

def pointDiff(pointA, pointB):
    #return dx, dy
    return [pointB[0] - pointA[0], pointB[1] - pointA[1]]

def getAllPoints(stroke):
    #stroke = list of ML,MLL,MLLL
    point_list = []
    for ind in range(len(stroke) - 1):
        x0, y0 = parsePointString(stroke[ind])
        x1, y1 = parsePointString(stroke[ind + 1])
        point_list += getPoints(x0, y0, x1, y1)
        point_list.pop() #avoid redundant points
    x1, y1 = parsePointString(stroke[-1])
    point_list += [[x1, y1]] #append last point
    # offset points to origin 0,0
    point_list = [tuple(point) for point in point_list]
    return point_list

#point class
class Point:
    '''
    class to represent simple point
    '''
    def __init__(self, x = None, y = None):
        if x == None and y ==  None:
            self.x = 0
            self.y = 0
        else:
            self.x = x
            self.y = y

    def updatePoint(self, point_string):
        #update X_loc
        points = parsePointString(point_string)
        self.x = points[0]
        self.y = points[1]
    def __str__(self):
        return "X : {} Y : {}\n".format(self.x, self.y)
    def __to_ndarray__():
        return np.array([self.x, self.y])
    def getPoints(self):
        return self.x, self.y

# image generator class
class ImageGen:
    '''
        Image Generator class, to apply shifting along x and y axis to images
        rough implementation for data augmention of grayscale images
        ex :
        datagen = ImageGen(width_shift = [-5,5]) # use any one transformation at a time
        datagen.flow(imgs) # imgs is list of images to apply transformations on, all images should have same dimensions

        datagen is iterator object, with __next__() method, for use in for loop
    '''
    def __init__(self, width_shift = None, heigth_shift = None): # width_shift = [-x, +x, step]
        self.width_shift = range(width_shift[0], width_shift[1], width_shift[2]).__iter__() if width_shift else None
        self.heigth_shift = range(heigth_shift[0], heigth_shift[1], heigth_shift[2]).__iter__() if heigth_shift else None

    def flow(self, imgs):
        self.imgs = imgs

    def __iter__(self):
        # return iterator object with __next__() method
        return self

    def __next__(self):
        # shift along x axis
        if self.width_shift:
            tx = next(self.width_shift)
            rows,cols = self.imgs[0].shape
            M = np.float32([[1,0,tx],[0,1,0]])
            dst_images = []
            for img in self.imgs:
                dst = cv.warpAffine(img,M,(cols,rows))
                dst_images.append(dst)
            return dst_images

        # shift along y axis
        if self.heigth_shift:
            ty = next(self.heigth_shift)
            rows,cols = imgs[0].shape
            M = np.float32([[1,0,ty],[0,1,0]])
            dst_images = []
            for img in self.imgs:
                dst = cv.warpAffine(img,M,(cols,rows))
                dst_images.append(dst)
            return dst_images
