#filename : visualize_dataset.py
#author : PRAJWAL T R
#date last modified : Thu Oct 29 16:42:53 2020
#comments :
'''
    visualise pickled global and local dataset
    script saves images in ./test_dir/<global/local>_pics/ so create one before running the script
    USAGE :
    $python visualise_dataset <dataset>

    <dataset> - g - Global
                l - Local
'''

import matplotlib.pyplot as plt
import numpy as np
from os import walk
from drawing_utils import *

global_dir_path = "./test_dir/global_pics/"
local_dir_path = "./test_dir/local_pics/"
traverse_path = "./kanji_modified/"
samples = 20

_,_,filelist = next(walk(traverse_path))

def help():
    print("USAGE : \n \
    $python visualise_dataset <dataset>\n \
    <dataset> - g - Global\n \
                l - Local\n \
                ga - Global Augmented")
    exit(0)

#argument processing
import sys
argv = sys.argv

if len(argv) != 2:
    help()

# vanilla dataset visualization
if argv[1].lower() == 'g':
    # plot and save global dataset
    from global_strokegenerator import strokeGenerator
    sg = strokeGenerator(filelist)
    for ind in range(samples):
        img, label = next(sg)
        #get label image
        label = np.reshape(label, (HEIGHT, WIDTH))
        img = np.transpose(img, (2,0,1))
        _, axs = plt.subplots(1, 5)
        axs[0].imshow(img[0], cmap="Greys_r")
        axs[1].imshow(img[1], cmap="Greys_r")
        axs[2].imshow(img[2], cmap="Greys_r")
        axs[3].imshow(img[3], cmap="Greys_r")
        axs[4].imshow(label, cmap="Greys_r")
        axs[0].set_title("X_loc")
        axs[1].set_title("X_env")
        axs[2].set_title("X_last")
        axs[3].set_title("X_diff")
        axs[4].set_title("label")
        plt.savefig(global_dir_path + "sample" + str(ind) + ".png")
        plt.close()
# visualise dataset if it was augmented
elif argv[1].lower() == 'ga':
    # plot and save global dataset
    from global_strokegenerator import strokeGenerator
    sg = strokeGenerator(filelist, True)
    for ind in range(samples):
        img, label = next(sg)
        #get label image
        label = np.reshape(label, (HEIGHT, WIDTH))
        img = np.transpose(img, (2,0,1))
        _, axs = plt.subplots(1, 5)
        axs[0].imshow(img[0], cmap="Greys_r")
        axs[1].imshow(img[1], cmap="Greys_r")
        axs[2].imshow(img[2], cmap="Greys_r")
        axs[3].imshow(img[3], cmap="Greys_r")
        axs[4].imshow(label, cmap="Greys_r")
        axs[0].set_title("X_loc")
        axs[1].set_title("X_env")
        axs[2].set_title("X_last")
        axs[3].set_title("X_diff")
        axs[4].set_title("label")
        plt.savefig(global_dir_path + "sample" + str(ind) + ".png")
        plt.close()
# local dataset visualization
else:
    from local_strokegenerator import *
    lg = strokeGenerator(filelist)
    # plot and save local dataset
    for ind in range(samples):
        img, ext, t, c_img = next(lg)
        c_img = np.reshape(c_img, (crop_img_size, crop_img_size))
        img = np.transpose(img, (2,0,1))
        _, axs = plt.subplots(1, 6)
        axs[0].imshow(img[0], cmap="Greys_r")
        axs[1].imshow(img[1], cmap="Greys_r")
        axs[2].imshow(img[2], cmap="Greys_r")
        axs[3].axis('off')
        axs[3].text(0.0, 0.5, repr(list(ext)))
        axs[4].axis('off')
        axs[4].text(0.0, 0.5, repr(list(t)))
        axs[5].imshow(c_img, cmap="Greys_r")

        axs[0].set_title("env_img")
        axs[1].set_title("diff_img")
        axs[2].set_title("con_img")
        axs[3].set_title("ext vector")
        axs[4].set_title("touch")
        axs[5].set_title("cropped_img")
        plt.savefig(local_dir_path + "sample" + str(ind) + ".png")
        plt.close()
