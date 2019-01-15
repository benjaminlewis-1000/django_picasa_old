#! /usr/bin/env python

from sklearn.cluster import AgglomerativeClustering as ac
import sklearn.cluster as cluster
import numpy as np
import time
import dlib
import pickle
from shutil import copyfile
from shutil import rmtree
from collections import Counter
import os
from PIL import Image

# Set up directories where pickled CNN classifications and original
# photos are located as well as a directory in which to put chips.
train_dir = '/mnt/data/samba_share/exclude/tagger_subset/pickles2x2/train'
train_photo_dir = '/mnt/data/samba_share/exclude/tagger_subset/train'
train_chip_dir = '/mnt/data/samba_share/exclude/tagger_subset/train_chips'
sorted_chip_dir = '/mnt/data/samba_share/exclude/tagger_subset/sorted_chips'

# Method that extracts the chip from the image based on the dictionary
# representation of the region of interst. Returns the numpy array chip.
def extractFace(dataDict, img):
    ts = dataDict['top_scaled']
    bs = dataDict['bottom_scaled']
    ls = dataDict['left_scaled']
    rs = dataDict['right_scaled']
    output = img[ts:bs, ls:rs]
#), 'right_scaled': 1894, 'height_face': 126, 'bottom_scaled': 1679, 'top_scaled': 1553, 'width_face': 125, 'left_scaled': 1769}]
    return output

# I want this pre-computed the first time, then able to be loaded after that.
# Run through the directory of pickled CNN results. If the pickle contains a
# face, put the 128-dimensional represnetation of the face into a numpy array
# as another row. Also extract the corresponding face chip to the chip directory.
# 
if not os.path.exists('pickle_list.pkl'):
    chipnames = []    
    enc_array = np.array([])
    num=0
    for root, dirs, paths in os.walk(train_dir):
        for fname in paths:
            num += 1
            if fname.endswith('pkl'):
                # Construct the path to the pickle file and load it
                fullpath = os.path.join(root, fname)
                data = pickle.load(open(fullpath, 'rb') )
                # Create an image name that corresponds to the 
                # pickle file name. Load it as a numpy array.
                imgname = os.path.join(train_photo_dir, fname[:-4] + '.jpg')
                np_img = np.array(Image.open(imgname))

                # For each face in the pickle, extract teh encoding. Chip out
                # the face from the corresponding image. Save the chip with a
                # suffix _<number> to the chip out directory. Add the chip 
                # name to a list. 
                for i in range(len(data)):
                    enc = data[i]['encoding']
                    chipname = "{}_{}.jpg".format(fname[:-4], i) 
                    chip = extractFace(data[i], np_img)
                    chip = Image.fromarray(chip.astype(np.uint8) )
                    chip.save(os.path.join(train_chip_dir, chipname) )
                    chipnames.append(chipname)
                    if len(enc_array) == 0:
                        enc_array = np.append(enc_array, enc)
                    else:
                        enc_array = np.vstack((enc_array, enc))
                
    
    # Save off the list of encodings as well as the names of chips 
    # in a pickle.
    with open('pickle_list.pkl', 'wb') as fh:
        pickle.dump(enc_array, fh, protocol=pickle.HIGHEST_PROTOCOL)
    with open('chiplist.pkl', 'wb') as fh:
        pickle.dump(chipnames, fh, protocol=pickle.HIGHEST_PROTOCOL)

else:
    enc_array = pickle.load(open('pickle_list.pkl', 'rb') )
    chipnames = pickle.load(open('chiplist.pkl', 'rb') )

def sortByLabels(chipnames, labels):
    rmtree(sorted_chip_dir)
    print('Sorting by labels!')
    if not os.path.exists(sorted_chip_dir):
        os.makedirs(sorted_chip_dir)
    for pair in zip(chipnames, labels):
        chipPath = os.path.join(train_chip_dir, pair[0])
        chipLabel = str(pair[1])
        sortPath = os.path.join(sorted_chip_dir, chipLabel)
        if not(os.path.exists(sortPath) ):
            os.makedirs(sortPath)
        copyfile(chipPath, os.path.join(sortPath, pair[0]))
        


doDB = False
doAggregate = False
doChinese = True
#enc_array = enc_array[:1000, :]
#chipnames = chipnames[:1000]
print(enc_array.shape)
print(len(chipnames))

# Different clustering algorithms
if doDB:
    start = time.time()
    
    dbCluster = cluster.DBSCAN(eps=0.5, min_samples=3)
    dbCluster.fit(enc_array[:, :])
    labels = dbCluster.labels_
    print(Counter(labels))
    sortByLabels(chipnames, labels)
    
    print("Elapsed time: {}".format(time.time() - start) )

if doAggregate:
    print("Doing aggregate")
    start = time.time()
    clustering = ac()
    nc = enc_array.shape[0] / 6
    nc = 500
    clustering.set_params(n_clusters=nc, linkage='ward')
    clustering.fit(enc_array)
    labels=clustering.labels_
    print(Counter(labels))
    sortByLabels(chipnames, labels)
    labels.sort()
    # print(labels)
    print("Elapsed time: {}".format(time.time() - start) )

if doChinese:
#    enc_array = enc_array[:1000, :]
    start = time.time()
    enc_list = [dlib.vector(enc_array[i, :]) for i in range(enc_array.shape[0])]
    labels = dlib.chinese_whispers_clustering(enc_list, 0.3)
    print("Elapsed time: {}".format(time.time() - start) )
    print(Counter(labels))
    sortByLabels(chipnames, labels)
    


