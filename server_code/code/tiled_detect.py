#! /usr/bin/env python

import cv2
import numpy as np
import itertools
from rectangleBen import Rectangle as rectangle
import time

# import pyexiv2
from .pyPicasaFaceXMP import picasaXMPFaceReader as pfr
import face_recognition

# For my particular GPU, I'm finding that I can upsize by 3x for a 280 * 420 image,
# or by 2x for a 350 * 530 image. 
# Experiments TBD on CPU

# params1 = {'upsample': 2, 'height': 600, 'width': 800}
params1 = {'upsample': 2, 'height': 600, 'width': 300}
# params2 = {'upsample': 3, 'height': 280, 'width': 420}

class FaceRect:
    def __init__(self, rectangle, encoding = None, name=None):
        self.rectangle = rectangle
        self.encoding = encoding
        self.name = name

    def __eq__(self, otherFace):
        return self.rectangle.intersectOverUnion(otherFace.rectangle) > 0.2

    def __hash__(self):
        return 5


def split_range(range_len, num_parts):
    # Given a range, split it into a number of approximately equal parts. 

    avg_len = float(range_len) / num_parts

    # Build in a 3% overlap
    three_percent = range_len * 0.03

    val_list = []
    for i in range(num_parts):
        val_list.append( int( i * avg_len ) )

    val_list.append(range_len)

    return val_list

def detect_pyramid(cv_image):

    # Parameterization
    start_time = time.time()
    params = params1
    max_pixels_per_chip = params['height'] * params['width']
    num_upsamples = params['upsample']


    height = cv_image.shape[0]
    width = cv_image.shape[1]

    num_pixels = height * width
    num_chips = float(num_pixels / max_pixels_per_chip)
    # print num_chips
    num_iters = np.sqrt(num_chips)

    # First, we can resize the whole thing to the number of pixels
    # represented by the height and width parameters. This should
    # make it possible to fit in the GPU and we can get the biggest,
    # hardest-to-miss faces.

    num_faces = 0
    
    faceList = []

    for cuts in [1, 3]: #range(1, int(num_iters), 2):
        # Get lists of left/right and top/bottom indices. 
        width_parts = split_range(width, cuts)
        height_parts = split_range(height, cuts)

        print(cuts)

        width_x_percent = int(0.06 * width / cuts )
        height_x_percent = int(0.06 * height / cuts )

        for leftIdx in range(len(width_parts) - 1):
            for topIdx in range(len(height_parts) - 1):

                left = width_parts[leftIdx]
                right = width_parts[leftIdx + 1]
                top = height_parts[topIdx]
                bottom = height_parts[topIdx + 1]

                # Since the faces may be split on an edge,
                # put in a 3% overlap between tiles.
                if left > 0: 
                    left -= width_x_percent
                if top > 0:
                    top -= height_x_percent
                if right < width:
                    right += width_x_percent
                if bottom < height:
                    bottom += height_x_percent

                chip_part = cv_image[top:bottom, left:right]
                print(chip_part.shape)
                height_chip = chip_part.shape[0]
                width_chip = chip_part.shape[1]
                pixels_here = height_chip * width_chip
                resize_ratio = np.sqrt( float( pixels_here ) / max_pixels_per_chip ) 

                resized_chip = cv2.resize(chip_part, \
                    ( int( width_chip / resize_ratio ), \
                      int( height_chip / resize_ratio ) ) )
                print(resized_chip.shape)
                face_locations = face_recognition.face_locations(resized_chip, \
                    number_of_times_to_upsample=num_upsamples,  model='cnn')

                identity = face_recognition.face_encodings(resized_chip, known_face_locations=face_locations, num_jitters=3)
                print("ID len: " + str(len(identity)))
                assert len(identity) == len(face_locations), 'Identity vector length != face location vector length.'

                num_faces += len(face_locations)
                print( num_faces )

                for index in range(len(face_locations)):
                    top_chip, right_chip, bottom_chip, left_chip = face_locations[index]
                    encoding = identity[index]

                    # top_scaled = top / (height_chip / resize_ratio)  * height_chip
                    top_scaled = int(top_chip * resize_ratio + top)
                    bottom_scaled = int(bottom_chip * resize_ratio + top)
                    left_scaled = int(left_chip * resize_ratio + left)
                    right_scaled = int(right_chip * resize_ratio + left)

                    height_face = np.abs(bottom_scaled - top_scaled)
                    width_face = np.abs(right_scaled - left_scaled)
                    # locRect = rec(left, top, right, bottom)
                    # face_image = image[top:bottom, left:right]
                    cv2.rectangle(cv_image, (left_scaled, top_scaled), (right_scaled, bottom_scaled), (0, 255, 0), 5)
                    # pil_image = Image.fromarray(face_image)
                    # pil_image.show()
                    rect = rectangle(height_face, width_face, leftEdge = left_scaled, topEdge = top_scaled)
                    face = FaceRect(rect, encoding, name=None)
                    faceList.append(face)

    print(len(faceList))
    print(len(set(faceList)))
    elapsed_time = time.time() - start_time
    print("Elapsed time is : " + str( elapsed_time ) )

    for eachFace in list(set(faceList)):
        pass
        r = eachFace.rectangle
        left = r.left
        right = r.right
        top = r.top
        bottom = r.bottom
        cv2.rectangle(cv_image, (left, top), (right, bottom), (255, 0, 0), 5)
        



    # Convert to OpenCV colors, get a resized window, and show image. 
#    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
#    cv2.namedWindow('Resized Window', cv2.WINDOW_NORMAL)
#    cv2.resizeWindow('Resized Window', 800, 600)
#    cv2.imshow('Resized Window', cv_image)
#    cv2.waitKey(0)

    print(num_faces)

    return faceList


def extractPicasa(cv_path):

    picasaMetadata = pfr.Imagedata(cv_path)
    xmpFaces = pfr.XMPFace(picasaMetadata).getFaces()

    print(xmpFaces)

    faceList = []

    for faces in xmpFaces:
        personName = faces[4]

        left = faces[0]
        top = faces[1]
        width = faces[2]
        height = faces[3]

        locRect = rectangle(height, width, leftEdge = left, topEdge = top)
        face = FaceRect(locRect, encoding=None, name=personName)

        faceList.append(face)

    print( len(faceList) )

    return faceList

def correlateFaces(imagePath):
    image = face_recognition.load_image_file(imagePath)

    # Get the faces from face_detection as well as from picasa. 
    cnnFaces = detect_pyramid(image)
    namedFaces = extractPicasa(imagePath)

    matchedCnnFaces = []
    for eachFace in namedFaces:
        # One liner to get all indices of matches from the list. 
        # I want to get all matches for detected faces given an already-tagged 
        # face. 
        indices = [idx for idx, x in enumerate(cnnFaces) if x == eachFace]
        # print indices

        # Most cases will be this - in which case, add the name to the detected 
        # face (so that it has all information) and add that face to the matched 
        # faces list. 
        if len(indices) == 1:
            matchFace = cnnFaces[indices[0]]
            matchFace.name = eachFace.name
            matchedCnnFaces.append(matchFace)

        # Rarer case, where the IOU is great enough for two closely-spaced face. 
        # Determine which face has the larger IOU and assume that one is the right face.
        elif len(indices) > 1:
            bestIdx = -1
            IntOverUnion = 0
            for i in indices:
                iou_calc = eachFace.rectangle.intersectOverUnion(cnnFaces[i].rectangle)
                if iou_calc > IntOverUnion:
                    bestIdx = i
            matchFace = cnnFaces[bestIdx]
            matchFace.name = eachFace.name
            matchedCnnFaces.append(matchFace)
        # No match found in the detected faces. This might be just a spurious label, 
        # or the image may have been rotated and the tagged face is no longer valid. 
        else:
            print ( "no match tbd" )
            # Probably here I would search the whole list for any match? --
            # No, because of the edge case where a "face" takes up the whole image,
            # in which case IOU would be non-zero but small. That would be useless. 


    # Use set magic to remove the matched faces from the list of detected faces, then
    # turn both sets into lists and return them. 
    cnnSet = set(cnnFaces)
    cnnMatchedSet =set(matchedCnnFaces)
    unmatchedSet = cnnSet - cnnMatchedSet

    matched = list(cnnMatchedSet)
    unmatched = list(unmatchedSet)

    return matched, unmatched


if __name__ == "__main__":
    path = '/home/benjamin/Desktop/photos_for_test/train/B+J-36wedding.jpg'

    matched, unmatched = correlateFaces(path)

#    print len( set(namedFaces).intersection(set(cnnFaces)) )

 #   nameSet = set(namedFaces)
    print( len(matched) )
    matchNames = [a.name for a in matched]
    print( matchNames )

    matchNames = [a.encoding[2:4] for a in matched]
    print( matchNames )
    # bb = list(nameSet - cnnSet)

# unnamedSet = (cnnSet - nameSet)
# namedSet = cnnSet - unnamedSet
#     # print split_range(300, 7)
