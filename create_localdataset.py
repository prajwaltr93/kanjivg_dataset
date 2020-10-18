#filename : create_localdataset.py
#author : PRAJWAL T R
#date last modified : Mon Jul 13 14:25:12 2020
#comments :

'''
    python script to create dataset for local model in paper "Teaching Robots to Draw"

    dataset structure :
        dataset : {
            lG_data : [
                [X_env, X_con, X_diff] ,
                ... ,
                ... ,
            ] ,
            lG_croppedimg : [
                [cropped_img],
                ... ,
                ... ,
            ]
            lG_extract : [
                [begin, size],
                ... ,
                ... ,
            ]
            lG_touch : [
                [touch],
                ... ,
                ... ,
            ]
        }

    //end of structure

    keywords :
        X_env : visited region
        X_con: continoulsy connected stroke
        X_diff: remaining strokes to draw
    lG : state of local model
'''

from drawing_utils import *
from os import walk
import pickle as pic

test_dir_path = "./test_dir/local_pics/"

traverse_path = "./kanji_modified/"
local_dataset_path = "./local_dataset/"
strokes_lost = 0 # counter

#dataset structure
dataset = {
    'lG_data' : [],
    'lG_extract' : [],
    'lG_touch' : [], #output
    'lG_croppedimg' : [] #output
}

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

def plotImages(*images):
    # plot images for verification
    ind = images[0]
    images = images[1] # just for convinience
    fig, axs = plt.subplots(1, len(images))

    for image, index in zip(images, range(len(images))):
        axs[index].imshow(image)
        axs[index].set_title("image :" + index.__str__())
    plt.savefig(test_dir_path + "local_dataset "+ ind.__str__() + ".png")

def getSliceWindow(current_xy):
    '''
        generate two variables begin and size for dynamice tensor slicing using tf.slice
    '''
    x, y = current_xy[0], current_xy[1]
    begin = [y - 2, x - 2 , 0] # zero slice begin channel dimension
    return np.array(begin)

def pickleLocalDataset(dataset, ind, collect_minority):
    # prefix m to indicate dataset with only minority classes touch = 0
    if collect_minority:
        out_path = local_dataset_path+"m_data_batch_"+str(ind)
    else:
        out_path = local_dataset_path+"data_batch_"+str(ind)
    fd = open(out_path,"wb")
    #convert list to numpy array ie : compatiable with tensorflow data adapter
    dataset['lG_data'] = np.array(dataset['lG_data'])
    dataset['lG_extract'] = np.array(dataset['lG_extract'])
    dataset['lG_touch'] = np.array(dataset['lG_touch'])
    dataset['lG_croppedimg'] = np.array(dataset['lG_croppedimg'])
    pic.dump(dataset,fd)
    print("dataset created at : ",out_path)
    #clear contents of dataset structure
    dataset['lG_data'] = []
    dataset['lG_extract'] = []
    dataset['lG_touch'] = []
    dataset['lG_croppedimg'] = []

if __name__ == "__main__":
    import sys
    collect_minority = True if sys.argv[1] == "minority" else False # collect samples with touch = 0
    if collect_minority:
        sample_rate = 100
        file_cap = 6000
    else:
        sample_rate = 10
        file_cap = 100
    _, _, filelist = next(walk(traverse_path))
    breaks = [i for i in range(0, len(filelist[:file_cap]), sample_rate)]
    for break_ind in range(len(breaks) - 1):
        for file in filelist[breaks[break_ind] : breaks[break_ind + 1]]:
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
                    continue # negative cordinates are not included in regex
                env_stroke = X_target[0 : m_indices[index]]
                try:
                    diff_stroke = X_target[m_indices[index + 1] : ]
                except:
                    diff_stroke = []
                env_canvas = drawStroke(env_stroke)
                diff_canvas = drawStroke(diff_stroke)
                env_l = []
                diff_l = points
                touch = 1
                con_img = drawStroke(stroke)
                if not collect_minority:
                    for ind in range(len(points) - 1):
                        current_xy = points[ind] # crop at this coordinate
                        next_xy = points[ind + 1] # mark at this coordinate
                        try:
                        # inputs
                            ext_inp = getSliceWindow(current_xy)
                            env_img = drawFromPointsRetImage(env_l, env_canvas)
                            diff_img = drawFromPointsRetImage(diff_l, diff_canvas)
                            # outputs
                            next_xy_img = getCroppedImage(next_xy, current_xy) # 5 * 5 image with one point drawn and cropped at current_xy
                            # plot images for verfication
                            # plotImages(ind,[con_img, env_img, diff_img, next_xy_img])
                            # update dataset
                            dataset['lG_data'].append(np.dstack((env_img, diff_img, con_img)))
                            dataset['lG_extract'].append(ext_inp)
                            dataset['lG_croppedimg'].append(np.reshape(next_xy_img, (crop_img_size * crop_img_size)))
                            dataset['lG_touch'].append(np.array([touch]))
                        except:
                            strokes_lost += 1
                        # update env,diffg
                        env_l = points[0 : ind + 2] # add two points for one complete stroke
                        diff_l = points[ind + 1 :]
                if collect_minority:
                    try:
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
                        dataset['lG_data'].append(np.dstack((env_img, diff_img, con_img)))
                        dataset['lG_extract'].append(ext_inp)
                        dataset['lG_croppedimg'].append(np.reshape(next_xy_img, (crop_img_size * crop_img_size)))
                        dataset['lG_touch'].append(np.array([touch]))
                    except:
                        strokes_lost += 1
        #save dataset to disk
        pickleLocalDataset(dataset,  break_ind, collect_minority)
    print("strokes lost : ", strokes_lost)
