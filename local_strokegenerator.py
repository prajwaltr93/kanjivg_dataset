#filename : local_strokegenerator.py
#author : PRAJWAL T R
#date last modified : Mon Oct 20 14:25:12 2020
#comments :

'''
    simple python generator that yields data required for training local model
'''

from os import walk
from drawing_utils import *

# traverse_path = "/content/drive/My Drive/train_local_model/kanji_modified/"

traverse_path = "/home/starkm42/kanjivg_dataset/kanji_modified/"

def getSliceWindow(current_xy):
    '''
        generate two variables begin and size for dynamice tensor slicing using tf.slice
    '''
    x, y = current_xy[0], current_xy[1]
    begin = [y - 2, x - 2 , 0] # zero slice begin channel dimension
    return np.array(begin)

def getCroppedImage(next_xy, current_xy):
    # create image with black background
    img = np.zeros((HEIGHT, WIDTH))
    # mark point with next_xy cordinates
    img[next_xy[1], next_xy[0]] = COLOR # open cv and numpy has different axis for x and y, also raises exception
    # crop at current_xy
    slice_begin = getSliceWindow(current_xy)[:-1]
    img = img[slice_begin[0]: slice_begin[0] + 5,slice_begin[1]:slice_begin[1] + 5]
    return img #return cropped image

# Stoke generator, one sample at a time
def strokeGenerator(filelist):
    for file in filelist:
        svg_string = open(traverse_path+file).read()
        X_target, m_indices = getStrokesIndices(svg_string)
        #loop through all strokes
        for index in range(len(m_indices)):
            # handle single strokes
            try:
                #get current stroke
                stroke = X_target[m_indices[index] : m_indices[index + 1]]
            except: # out of index exception, last and beyond
                stroke = X_target[m_indices[index] : ]
            #all points for given stroke ML,MLL,MLLLL
            points = getAllPoints(stroke)
            env_stroke = X_target[0 : m_indices[index]]
            try:
                diff_stroke = X_target[m_indices[index + 1] : ]
            except:
                diff_stroke = []
            env_canvas = drawStrokeL(env_stroke)
            diff_canvas = drawStrokeL(diff_stroke)
            env_l = []
            diff_l = points
            touch = 1
            con_img = drawStrokeL(stroke)
            for ind in range(len(points) - 1):
                current_xy = points[ind] # crop at this coordinate
                next_xy = points[ind + 1] # mark at this coordinate
                # inputs
                ext_inp = getSliceWindow(current_xy)
                env_img = drawFromPointsRetImage(env_l, env_canvas)
                diff_img = drawFromPointsRetImage(diff_l, diff_canvas)
                # outputs
                next_xy_img = getCroppedImage(next_xy, current_xy) # 5 * 5 image with one point drawn and cropped at current_xy
                # plot images for verfication
                # plotImages(ind,[con_img, env_img, diff_img, next_xy_img])
                # update dataset
                yield np.dstack((env_img, diff_img, con_img)), ext_inp, np.array([touch]), next_xy_img
                # update env,diffg
                env_l = points[0 : ind + 2] # add two points for one complete stroke
                diff_l = points[ind + 1 :]
            # update last instance
            touch = 0
            env_l = points
            diff_l = []
            current_xy = points[-1]
            # inputs
            # con_img
            ext_inp = getSliceWindow(current_xy)
            env_img = drawFromPointsRetImage(env_l, env_canvas)
            diff_img = drawFromPointsRetImage(diff_l, diff_canvas)
            # update dataset
            # check if cordinates are valid by testing slicing at current_xy, if it does not return 5 * 5 image then discard
            next_xy_img = getCroppedImage(current_xy, current_xy) # using defualt class
            yield np.dstack((env_img, diff_img, con_img)), ext_inp, np.array([touch]), next_xy_img
