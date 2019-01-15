#! /usr/bin/env python

import PIL
from PIL.ExifTags import TAGS 
from PIL import Image
import os
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage

def loadImageOriented(filePath):
    print filePath
    image = Image.open(filePath)
    exifDict = {}
    info = image._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        exifDict[decoded] = value
    orientation = exifDict['Orientation']
    print orientation
    np_image = np.array(image)

    def mirrorAcrossVertical(np_img_array):
        np_img_array = np.fliplr(np_img_array)
        return np_img_array

    def mirrorAcrossHorizon(np_img_array):
        np_img_array = np.flipud(np_img_array)
        return np_img_array

    def rotate_cw(np_img_array, degrees_cw):
        # ndimage rotate rotates counter clockwise, but EXIF
        # defines rotation by degrees clockwise. 
        # Need to recast
        degrees_ccw = (360 - degrees_cw) % 360
        np_img_array = ndimage.rotate(np_img_array, degrees_ccw) 
        return np_img_array

    # Rotate / flip the image according to EXIF instructions. 
    # Name the output to oriented_img.
    if orientation == 1:
        # No rotation
        oriented_img = np_image
    elif orientation == 2:
        # Mirror across vertical
        oriented_img = mirrorAcrossVertical(np_image)

    elif orientation == 3:
        # Rotate 180
        oriented_img = rotate_cw(np_image, 180)

    elif orientation == 4:
        # Mirror across horizon
        oriented_img = mirrorAcrossHorizon(np_image)

    elif orientation == 5:
        # Mirror across vertical, rotate 270 CW
        np_image = mirrorAcrossVertical(np_image)
        oriented_img = rotate_cw(np_image, 270)

    elif orientation == 6:
        # Rotate 90 CW
        oriented_img = rotate_cw(np_image, 90)

    elif orientation == 7:
        # Mirror across vertical, rotate 90 CW
        np_image = mirrorAcrossVertical(np_image)
        oriented_img = rotate_cw(np_image, 90)

    elif orientation == 8:
        # Rotate 270 CW
        oriented_img = rotate_cw(np_image, 270)

    return oriented_img


if __name__ == '__main__':
    # rootPath = 
    rootPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    orientPath = os.path.join(rootPath, 'test_imgs', 'orientation')
    for root, dirs, fnames in os.walk(orientPath):
        for eachFile in fnames:
            filename = os.path.join(root, eachFile)
            img = loadImageOriented(filename)
            print(img.shape)
            plt.imshow(img, interpolation='nearest')
            plt.show()