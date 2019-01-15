#! /usr/bin/env python

import os
from code.tiled_detect import detect_pyramid
import pickle
import numpy as np
from detector import detector

# import concurrent.futures
import face_recognition

root = '/mnt/NAS/exclude/tagger_subset/'
rootDir = os.path.join(root, 'test')
pickleSaveDir3 = os.path.join(root, 'pickles3x3/test')
pickleSaveDir2 = os.path.join(root, 'pickles2x2/test')
trrootDir = os.path.join(root, 'train')
trpickleSaveDir3 = os.path.join(root, 'pickles3x3/train')
trpickleSaveDir2 = os.path.join(root, 'pickles2x2/train')
print(trrootDir)
assert os.path.isdir(trrootDir)
assert os.path.isdir(trpickleSaveDir2)
assert os.path.isdir(trpickleSaveDir3)

listOfFilesToProcess = []

assert os.path.isdir(rootDir)
assert os.path.isdir(pickleSaveDir2)
assert os.path.isdir(pickleSaveDir3)

for root, dirname, fnames in os.walk(rootDir):
    for file in fnames:
        fullpath = os.path.join(root, file)
        
        pkl_file = file[:-3] + 'pkl'
        pickle_fullname3 = os.path.join(pickleSaveDir3, pkl_file)
        pickle_fullname2 = os.path.join(pickleSaveDir2, pkl_file)

        if not os.path.exists(pickle_fullname3):
            listOfFilesToProcess.append( (fullpath, pickle_fullname3, pickle_fullname2) )


for root, dirname, fnames in os.walk(trrootDir):
    for file in fnames:
        fullpath = os.path.join(root, file)
        
        pkl_file = file[:-3] + 'pkl'
        pickle_fullname3 = os.path.join(trpickleSaveDir3, pkl_file)
        pickle_fullname2 = os.path.join(trpickleSaveDir2, pkl_file)

        if not os.path.exists(pickle_fullname3):
            listOfFilesToProcess.append( (fullpath, pickle_fullname3, pickle_fullname2) )

filelist = np.random.permutation(listOfFilesToProcess)
print(len(filelist))

def processImage(file_tuple):
    jpeg = file_tuple[0]
    pkl3x3 = file_tuple[1]
    pkl2x2 = file_tuple[2]
    print(jpeg)

    det = detector(jpeg, numpartitions=2)
    faceList2 = det.detect_pyramid()
    with open(pkl2x2, 'wb') as fh:
        pickle.dump(faceList2, fh, protocol=pickle.HIGHEST_PROTOCOL)

    det = detector(jpeg, numpartitions=3)
    faceList3 = det.detect_pyramid()
    with open(pkl3x3, 'wb') as fh:
        pickle.dump(faceList3, fh, protocol=pickle.HIGHEST_PROTOCOL)

for file_tuple in filelist:
    processImage(file_tuple)

