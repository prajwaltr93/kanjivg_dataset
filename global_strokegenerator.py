#filename : global_strokegenerator.py
#author : PRAJWAL T R
#date last modified : Fri Oct 23 22:17:26 2020
#comments :

'''
    python generator for global model, yields samples for training global model
'''
import numpy as np
from drawing_utils import *

traverse_path = "./kanji_modified/"

# Stroke generator, one sample at a time
def strokeGenerator(filelist):
    for file in filelist:
        svg_string = open(traverse_path+file).read()
        X_target, m_indices = getStrokesIndices(svg_string)
        # last point of local model
        X_loc = Point()
        # strokes completed by local model
        X_env = []
        # last stroke drawn by local model
        X_last = []
        # remaining strokes to complete
        X_diff = X_target
        #target label
        label = Point()
        label.updatePoint(X_target[0])
        # creating images and labels
        for index, m_index in zip(range(len(m_indices)), m_indices.__iter__()):
            # each function call generates corresponding image
            X_loc_img = drawPoint(X_loc)
            X_env_img = drawStroke(X_env)
            X_last_img = drawStroke(X_last)
            X_diff_img = drawStroke(X_diff)
            X_label_img = drawPoint(label)
            yield np.dstack((X_loc_img, X_env_img, X_last_img, X_diff_img)), np.reshape(X_label_img, (HEIGHT * WIDTH))
            # udpate variables
            if (len(m_indices) == 1) or (index + 1 == len(m_indices)):
                # X_target has only one stroke
                continue
            X_loc.updatePoint(X_target[m_indices[index + 1] - 1])
            X_env += X_target[m_indices[index] : m_indices[index + 1]]
            X_last = X_target[m_indices[index] : m_indices[index + 1]]
            X_diff = X_target[m_indices[index + 1]:]
            label.updatePoint(X_target[m_indices[index + 1]])
