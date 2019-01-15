#! /usr/bin/env python

import cv2
import numpy as np
import itertools
import time

import face_recognition

# For my particular GPU, I'm finding that I can upsize by 3x for a 280 * 420 image,
# or by 2x for a 350 * 530 image. 
# Experiments TBD on CPU

# params1 = {'upsample': 2, 'height': 600, 'width': 800}
# params2 = {'upsample': 3, 'height': 280, 'width': 420}


class detector():
    def __init__(self, filename, numpartitions = 3):
        self.image = face_recognition.load_image_file(filename)
        self.detector_params = {'upsample': 2, 'height': 600, 'width': 300}
        self.numpartitions = numpartitions

    def split_range(self, range_len, num_parts):
        # Given a range, split it into a number of approximately equal parts. 
        avg_len = float(range_len) / num_parts
        # Build in a 3% overlap
        three_percent = range_len * 0.03
        val_list = []
        for i in range(num_parts):
            val_list.append( int( i * avg_len ) )
        val_list.append(range_len)

        return val_list

    def detect_pyramid(self):

        # Parameterization
        start_time = time.time()
        max_pixels_per_chip = self.detector_params['height'] * self.detector_params['width']
        num_upsamples = self.detector_params['upsample']

        height = self.image.shape[0]
        width = self.image.shape[1]

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

        for cuts in [1, self.numpartitions]:
            # Get lists of left/right and top/bottom indices. 
            width_parts = self.split_range(width, cuts)
            height_parts = self.split_range(height, cuts)

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

                    chip_part = self.image[top:bottom, left:right]
                    # print(chip_part.shape)
                    height_chip = chip_part.shape[0]
                    width_chip = chip_part.shape[1]
                    pixels_here = height_chip * width_chip
                    resize_ratio = np.sqrt( float( pixels_here ) / max_pixels_per_chip ) 

                    resized_chip = cv2.resize(chip_part, \
                        ( int( width_chip / resize_ratio ), \
                          int( height_chip / resize_ratio ) ) )
                    # print(resized_chip.shape)
                    face_locations = face_recognition.face_locations(resized_chip, \
                        number_of_times_to_upsample=num_upsamples,  model='cnn')

                    identity = face_recognition.face_encodings(resized_chip, known_face_locations=face_locations, num_jitters=3)
                    # print("ID len: " + str(len(identity)))
                    assert len(identity) == len(face_locations), 'Identity vector length != face location vector length.'

                    num_faces += len(face_locations)
                    # print( num_faces )

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

                        valDict = {}
                        valDict['height_face'] = height_face
                        valDict['width_face'] = width_face
                        valDict['top_scaled'] = top_scaled
                        valDict['bottom_scaled'] = bottom_scaled
                        valDict['left_scaled'] = left_scaled
                        valDict['right_scaled'] = right_scaled
                        valDict['encoding'] = encoding

                        faceList.append(valDict)

        print(len(faceList))
        # print(len(set(faceList)))
        elapsed_time = time.time() - start_time
        print("Elapsed time is : " + str( elapsed_time ) )


        return faceList


if __name__ == "__main__":
    import pickle
    path = '/mnt/data/samba_share/exclude/tagger_subset/train/1152.jpg'

    det = detector(path, numpartitions = 2)
    faceList = det.detect_pyramid()

    with open('test.pkl', 'wb') as fh:
        pickle.dump(faceList, fh, protocol=pickle.HIGHEST_PROTOCOL)
