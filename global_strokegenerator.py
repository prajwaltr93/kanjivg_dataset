#filename : global_strokegenerator.py
#author : PRAJWAL T R
#date last modified : Fri Oct 23 22:17:26 2020
#comments :

'''
    python generator for global model, yields samples for training global model
'''
import numpy as np
from drawing_utils import *
import copy as cp

traverse_path = "./kanji_modified/"

# Stroke generator, one sample at a time
def strokeGenerator(filelist, dataaug = False):
    for file in filelist:
        svg_string = open(traverse_path+file).read()
        X_target = getStrokes(svg_string)
        # last point of local model
        X_loc = Point()
        # strokes completed by local model
        X_env = []
        # last stroke drawn by local model
        X_last = []
        # remaining strokes to complete
        X_diff = cp.deepcopy(X_target)
        #target label
        label = Point()
        label.updatePoint(X_target[0][0])
        # creating images and labels
        for ind in range(len(X_target)):
            # each function call generates corresponding image
            stroke = X_target[ind]
            X_loc_img = drawPoint(X_loc)
            X_env_img = drawStroke(X_env)
            X_last_img = drawStroke(X_last)
            X_diff_img = drawStroke(X_diff)
            X_label_img = drawPoint(label)

            yield np.dstack((X_loc_img, X_env_img, X_last_img, X_diff_img)), np.reshape(X_label_img, (HEIGHT * WIDTH))
            # configure image data augementation if specified
            auggen = ImageGen(width_shift=[-2, 3, 1], height_shift=[-2, 3, 1]) if dataaug else None # 5 steps from -2 to 2 total of 5 augmented images applied randomly.
            # get augmented images if configured
            if auggen:
                auggen.flow([X_loc_img, X_env_img, X_last_img, X_diff_img, X_label_img])
                for X_loc_img, X_env_img, X_last_img, X_diff_img, X_label_img in auggen:
                    yield np.dstack((X_loc_img, X_env_img, X_last_img, X_diff_img)), np.reshape(X_label_img, (HEIGHT * WIDTH))
            # udpate variables
            if(ind+1 == len(X_target)): # reached end of strokes
                continue # excluding last step of argmax(label) = 0 TODO : consider this step also ?
            X_loc.updatePoint(stroke[-1])
            X_env += [stroke]
            X_last = [stroke]
            X_diff.pop(0) # remove first stroke
            label.updatePoint(X_target[ind +1][0]) # next stroke first cordinate
