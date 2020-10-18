#filename : create_metadata.py
#author : PRAJWAL T R
#date last modified : Sat Sep 12 22:25:16 2020
#comments :

'''
    script to get metadata such as input/output dimension, number of samples
    in train, test and validation sets for both global and local datasets.

    USAGE:
    $python create_metadata.py <dataset> <train> <validation> <test>

    dataset - L -> Local Dataset
              G -> Global Dataset
    <test>,
    <test>,
    <train> - integer number of files to consider to count samples
'''

import sys
from drawing_utils import *
import pickle as pic
import copy as cp
from threading import Thread

global_dataset_path = "./global_dataset/"
local_dataset_path = "./local_dataset/"
prefix_norm = 'data_batch_'
prefix_minority = 'm_data_batch_'
NUM_THREADS = 4

def help():
    print("$python create_metadata.py <dataset> <train> <validation> <test> \n \
    dataset - L -> Local Dataset \n \
              G -> Global Dataset \n \
              L1 -> Local Dataset minority class \n \
    <train>, \n \
    <validation>, \n \
    <test> - integer number of files to consider to count samples")
    exit(0)

if len(sys.argv) != 5:
    print("not enough arguements")
    help() # print help and return

# argument processing
try:
    if sys.argv[1].lower() == 'g':
        path = global_dataset_path
        prefix = prefix_norm
        metadata = {
                    'train_samples' : 0,
                    'validation_samples' : 0,
                    'test_samples' : 0,
                    'img_dim' : [HEIGHT, WIDTH],
                    'label_dim' : HEIGHT * WIDTH
        }
    elif sys.argv[1].lower() == 'l':
        path = local_dataset_path
        prefix = prefix_norm
        #meta-data structure
        metadata = {
            "img_dim" : [HEIGHT, WIDTH],
            "target_img_dim" : crop_img_size*crop_img_size,
            "slice_tensor_dim" : 3,
            "train_samples" : 0,
            "validation_samples" : 0,
            "test_samples" : 0
        }
    elif sys.argv[1].lower() == 'l1':
        path = local_dataset_path
        prefix = prefix_minority
        # meta-data structure
        metadata = {
            "img_dim" : [HEIGHT, WIDTH],
            "target_img_dim" : crop_img_size*crop_img_size,
            "slice_tensor_dim" : 3,
            "train_samples" : 0,
            "validation_samples" : 0,
            "test_samples" : 0
        }
    else:
        help()
except:
    help()

try:
    train = int(sys.argv[2])
    validation = int(sys.argv[3])
    test = int(sys.argv[4])
except:
    # train, test, validation should be integers
    help()

from os import walk

_, _, filelist = next(walk(path))
if (train + validation + test) > len(filelist):
    print("Found {} data files, requested for {} files".format(len(filelist) - 1, train + test + validation))
    exit(0)

if sys.argv[1].lower() == 'g':
    train_files = ["train_" + prefix+i.__str__() for i in range(train)] #two files
    validation_files = ["validation_"+prefix+(i).__str__() for i in range(validation)]
    test_files = ["test_"+prefix+(i).__str__() for i in range(test)]
if sys.argv[1].lower() == 'l' or sys.argv[1].lower() == 'l1':
    train_files = [prefix+i.__str__() for i in range(train)] #two files
    validation_files = [prefix+(train+i).__str__() for i in range(validation)]
    test_files = [prefix+(train+validation+i).__str__() for i in range(test)]

traverse_values = ['train_samples', 'validation_samples', 'test_samples']

def thread_traverse(traverse_list, traverse_values, metadata):

    for fold, fold_value in zip(traverse_list, traverse_values):
        temp_len = 0
        for file in fold:
            print('current file : ', file)
            data = pic.load(open(path + file, 'rb'), encoding = 'bytes')
            temp_len += len(data[list(data.keys())[0]])
        metadata[fold_value] = temp_len
    return metadata

# deploy threads
train_unit = len(train_files) // NUM_THREADS if (len(train_files) % 4 == 0 and len(train_files) > 4) else ((len(train_files) // NUM_THREADS + 1) if (len(train_files) > 4) else len(train_files))
validation_unit = len(validation_files) // NUM_THREADS if (len(validation_files) % 4 == 0 and len(validation_files) > 4) else ((len(validation_files) // NUM_THREADS + 1) if (len(validation_files) > 4) else len(validation_files))
test_unit = len(test_files) // NUM_THREADS if (len(test_files) % 4 == 0 and len(test_files) > 4) else ((len(test_files) // NUM_THREADS + 1) if (len(test_files) > 4) else len(test_files))

thread_list = []
for mul in range(NUM_THREADS):
    traverse_list = [train_files[mul * train_unit : (mul + 1) * train_unit], validation_files[mul * validation_unit : (mul + 1) * validation_unit], test_files[mul * test_unit : (mul + 1) * test_unit]]
    x = Thread(target = thread_traverse, args = (traverse_list, traverse_values, metadata))
    x.start()
    print("Thread %d covering train : %d validation %d test %d files" % (mul, len(traverse_list[0]), len(traverse_list[1]), len(traverse_list[2])))
    thread_list.append(x)

for thread in thread_list:
    thread.join() # wait for each thread to finish

# print generated metadata to output
for key, item in metadata.items():
    print(key, item)

# pickle dataset
fd = open(path + prefix + "metadata", 'wb')
pic.dump(metadata, fd)
print('metadata created at : ' + path + prefix +'metadata')
