#filename : create_localdataset.py
#author : PRAJWAL T R
#date last modified : Mon OCT 19 14:25:12 2020
#comments :

'''
    remove files not compatiable with dataset creation
'''

from drawing_utils import *
from os import walk

traverse_path = "./kanji_modified/"
sample_rate = 100
filelist_rem = []

def getCroppedImage(next_xy, current_xy):
    # create image with black background
    img = np.zeros((HEIGHT, WIDTH))
    # mark point with next_xy cordinates
    img[next_xy[1], next_xy[0]] = COLOR # open cv and numpy has different axis for x and y, also raises exception
    # crop at current_xy
    slice_begin = getSliceWindow(current_xy)[:-1]
    img = img[slice_begin[0]: slice_begin[0] + 5,slice_begin[1]:slice_begin[1] + 5]
    # # padding to ensure 5*5 image
    if img.shape != (5,5):
        raise
    #     rem_x, rem_y = crop_img_size - img.shape[0], crop_img_size - img.shape[1]
    #     img = cv.copyMakeBorder(img, 0, rem_x, 0, rem_y, cv.BORDER_CONSTANT, None, 0)
    return img #return cropped image

def getSliceWindow(current_xy):
    '''
        generate two variables begin and size for dynamice tensor slicing using tf.slice
    '''
    x, y = current_xy[0], current_xy[1]
    begin = [y - 2, x - 2 , 0] # zero slice begin channel dimension
    return np.array(begin)

def checkFileCompaitability(filelist):
    for file in filelist:
        svg_string = open(traverse_path+file).read()
        X_target, m_indices = getStrokesIndices(svg_string)
        #loop through all strokes
        for index in range(len(m_indices)):
            # handle single strokes
            try:
                #get current stroke
                stroke = X_target[m_indices[index] : m_indices[index + 1]]
            except: # out of index exception
                stroke = X_target[m_indices[index] : ]
            #all points for given stroke ML,MLL,MLLLL
            try:
                points = getAllPoints(stroke)
            except:
                print("negative cordinates : ", file)
                filelist_rem.append(file)
                break # negative cordinates are not included in regex

            for ind in range(len(points) - 1):
                current_xy = points[ind] # crop at this coordinate
                next_xy = points[ind + 1] # mark at this coordinate
                try:
                    next_xy_img = getCroppedImage(next_xy, current_xy) # 5 * 5 image with one point drawn and cropped at current_xy
                except:
                    print("no 5 * 5 images : ", file)
                    filelist_rem.append(file)
                    break
            try:
                current_xy = points[-1]
                # inputs
                next_xy_img = getCroppedImage(current_xy, current_xy) # using defualt class
            except:
                print("same : ",file)
                filelist_rem.append(file)

if __name__ == "__main__":
    _, _, filelist = next(walk(traverse_path))
    checkFileCompaitability(filelist)
    print("number of files not compaitable : ",len(set(filelist_rem)))
    print("press y to remove n to continue : ")
    if input().lower() == 'y':
        from os import remove
        for file in set(filelist_rem):
            remove(traverse_path+file)
            print("file removed : " + file)
