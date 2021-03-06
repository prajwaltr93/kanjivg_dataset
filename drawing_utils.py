#filename : drawing_utils.py
#author : PRAJWAL T R
#date last modified : Mon Jul  13 11:09:55 2020
#comments :

'''
    simple module with some basic drawing functions and user defined datatypes ex : Point and ImageGen
'''

import cv2 as cv
import re
import matplotlib.pyplot as plt
import numpy as np
from bresenhamsalgo import getPoints
import copy as cp
from random import shuffle
import itertools

# globals
WIDTH = 100
HEIGHT = 100
COLOR = 1
crop_img_size = 5
THICKNESS = 1
LINE_TYPE = cv.LINE_AA
path_re = re.compile(r"<path.*=\s'\s(.*)\s'.*/>")
command_re = re.compile(r"([M,L]\s\d+,\s\d+)")
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
def highlightPoints(points):
    # mark white points on black background
    img = np.zeros((HEIGHT, WIDTH))

    for point in points:
        img[point[1]][point[0]] = 1 # inverted x,y axis

    return img

def get2DCordinatesGlobal(index):
    '''
        convert index of flattened array to index of 2d array ex : 100 * 100 image
        return x,y
    '''
    return (index%HEIGHT, index//WIDTH)

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
    for stroke in strokes:
        for ind in range(len(stroke) - 1):
            cv.line(img, stroke[ind], stroke[ind+1],COLOR,THICKNESS,LINE_TYPE)
    return img

def drawStrokeL(strokes):
    '''
        given an stroke ex : MLL find m indices and draw stroke to image and return
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

def getStrokes(svg_string):
    '''
        get all M, L commands and collect index of each M command for global model
    '''
    strokes = path_re.findall(svg_string) # get all path elements with d attributes
    strokes = [list(map(lambda x : (int(x[0]), int(x[1])), points_re.findall(stroke))) for stroke in strokes] # remove svg instruction and retain points and convert them ints
    return strokes

def getStrokesIndices(svg_string):
    '''
        get all M, L commands and collect index of each M command for local model
        # TODO : unify both global and local stroke with common getStrokes function
    '''
    strokes = path_re.findall(svg_string) # get all path elements with d attributes
    X_target = []
    for stroke in strokes:
        command = command_re.findall(stroke)
        X_target += command
    m_indices = []
    for search_ind, path in zip(range(len(X_target)),X_target.__iter__()):
        if path[0] == 'M': # if command begins with M
            m_indices.append(search_ind)
    return X_target, m_indices

def drawFromPointsRetImage(points, img):
    '''
        over write on existing image, used to retain changes made by previous commands drawn
    '''
    # copy image
    img = cp.deepcopy(img)
    #if points = empty then return blank image
    if len(points) == 0:
        return img
    #else draw for each point
    for ind in range(len(points) - 1):
        cv.line(img, points[ind], points[ind + 1],COLOR, THICKNESS, LINE_TYPE)
    return img

def drawFromPoints(points):
    '''
        given points in list of x,y tuple, draw image using cv draw functions
    '''
    # if points not in tuple described in tuple
    if not points[0] == tuple():
        points = cp.deepcopy(points)
        points = [tuple(point) for point in points]

    img = np.zeros((HEIGHT, WIDTH))

    #if points = empty then return blank image
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
    '''
        segments given line stroke into points with interval difference in range[-2, 2] using bresenhams algorithm
    '''
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

    def updatePoint(self, points):
        #update X_loc
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
        datagen = ImageGen(width_shift = [-5,5,1], height_shift = [-5,5,1]),imgs is list of images to apply transformations on, all images should have same dimensions
        datagen is a iterator object, with __next__() method, for use in for loop
        this class should only be used for training global model
    '''
    def __init__(self, width_shift = None, height_shift = None): # width_shift = [-x, +x, step]
        self.dw = [w for w in range(width_shift[0], width_shift[1], width_shift[2])] if width_shift else [0]
        self.dh = [h for h in range(height_shift[0], height_shift[1], height_shift[2])] if height_shift else [0]

    def flow(self, imgs):
        # images to apply transformation
        self.imgs = imgs
        # return all combination of tx, ty
        combo = list(itertools.product(self.dw, self.dh))
        # remove (0, 0) from list, default transformation
        combo.remove((0, 0))
        # check if any given tansorformation can be performed without crossing frame for x_label, x_loc
        point_xloc = get2DCordinatesGlobal(np.argmax(np.reshape(imgs[2], imgs[2].shape[0] * imgs[2].shape[0])))
        point_xlabel = get2DCordinatesGlobal(np.argmax(np.reshape(imgs[4], imgs[4].shape[0] * imgs[4].shape[0])))
        # test every combination
        res_combo = []
        for txty in combo:
            x, y = txty
            if((point_xloc[0] + x) >= 0 and (point_xloc[0] + x) < HEIGHT and (point_xloc[1] + y) >= 0 and (point_xloc[1] + y) < WIDTH and (point_xlabel[0] + x) >= 0 and (point_xlabel[0] + x) < HEIGHT and (point_xlabel[1] + y) >= 0 and (point_xlabel[1] + y) < WIDTH):
                res_combo.append(txty)
        shuffle(res_combo) # randomise combinations
        self.txty = res_combo.__iter__() # object with __next__() method
        # TODO : applying shear transformation

    def __iter__(self):
        # return iterator object with __next__() method
        return self

    def __next__(self):
        # yield transformed images
        tx, ty = next(self.txty)
        rows,cols = self.imgs[0].shape
        M = np.float32([[1, 0, tx],[0, 1, ty]])
        dst_images = []
        for img in self.imgs:
            dst = cv.warpAffine(img,M,(cols,rows))
            dst_images.append(dst)
        return dst_images
