#filename : visualise_dataset.py
#author : PRAJWAL T R
#date last modified : Sun Jul  5 09:22:30 2020
#comments :
'''
    visualise pickled global and local dataset
    script saves images in ./test_dir/<global/local>_pics/ so create one before running the script
    USAGE :
    $python visualise_dataset <dataset>

    <dataset> - g - Global
                l - Local
'''

import pickle as pic
import matplotlib.pyplot as plt
import numpy as np
from drawing_utils import *

global_dataset_path = "./global_dataset/train_data_batch_1"
local_dataset_path = "./local_dataset/data_batch_1"

global_dir_path = "./test_dir/global_pics/"
local_dir_path = "./test_dir/local_pics/"

# magic numbers
start = 21
end = 49

def help():
    print("USAGE : \n \
    $python visualise_dataset <dataset>\n \
    <dataset> - g - Global\n \
                l - Local")
    exit(0)

#argument processing

import sys

argv = sys.argv

if len(argv) != 2:
    help()
if argv[1].lower() == 'g':
    data = pic.load(open(global_dataset_path,"rb"), encoding="bytes")

    imgs = data['sG_data'][start:end]

    labels = data['sG_labels'][start:end]

    print("input shape : ",np.shape(imgs[0]))
    print("label shape : ",np.shape(labels[0]))

    for img, label, ind in zip(imgs, labels, range(len(labels))):
        #get label image
        label = np.reshape(label,(HEIGHT, WIDTH))
        img = np.transpose(img,(2,0,1))
        _, axs = plt.subplots(1,5)
        axs[0].imshow(img[0],cmap="Greys_r")
        axs[1].imshow(img[1],cmap="Greys_r")
        axs[2].imshow(img[2],cmap="Greys_r")
        axs[3].imshow(img[3],cmap="Greys_r")
        axs[4].imshow(label,cmap="Greys_r")
        axs[0].set_title("X_loc")
        axs[1].set_title("X_env")
        axs[2].set_title("X_last")
        axs[3].set_title("X_diff")
        axs[4].set_title("label")
        plt.savefig(global_dir_path + "sample" + str(ind) + ".png")
else:

    data = pic.load(open(local_dataset_path,"rb"), encoding="bytes")
    imgs = data['lG_data'][start:end]
    extract = data['lG_extract'][start:end]
    touch = data['lG_touch'][start:end]
    cropped_img = data['lG_croppedimg'][start:end]

    print("image stack shape : ",np.shape(imgs[0]))
    print("cropped_img shape : ",np.shape(cropped_img[0]))
    print("touch vector shape : ",np.shape(touch[0]))
    print("extract vector shape : ",np.shape(extract[0]))

    for img, c_img, ext, t, ind in zip(imgs, cropped_img, extract, touch, range(len(imgs))):
        #get label image
        c_img = np.reshape(c_img,(crop_img_size, crop_img_size))
        img = np.transpose(img,(2,0,1))
        _, axs = plt.subplots(1,6)
        axs[0].imshow(img[0],cmap="Greys_r")
        axs[1].imshow(img[1],cmap="Greys_r")
        axs[2].imshow(img[2],cmap="Greys_r")
        axs[3].axis('off')
        axs[3].text(0.0, 0.5, repr(list(ext)))
        axs[4].axis('off')
        axs[4].text(0.0, 0.5, repr(list(t)))
        axs[5].imshow(c_img,cmap="Greys_r")

        axs[0].set_title("env_img")
        axs[1].set_title("diff_img")
        axs[2].set_title("con_img")
        axs[3].set_title("ext vector")
        axs[4].set_title("touch")
        axs[5].set_title("cropped_img")
        plt.savefig(local_dir_path + "sample" + str(ind) + ".png")
        plt.close()
