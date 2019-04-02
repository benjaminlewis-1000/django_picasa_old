
#! /usr/bin/env python

import os
import re
import PIL
from PIL import Image
import cv2

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))

class JPEG_metadata():
    """docstring for JPEG_metadata"""
    def __init__(self, filename):
        self.filename = filename

        assert os.path.exists(self.filename)
        assert re.match(".*\.[j|J][p|P][e|E]?[g|G]$", self.filename), 'Filename must end in some variant of "JPEG".'
    
        self.file_dir = os.path.dirname( os.path.normpath( self.filename) )

        self.PIL_img = Image.open(self.filename)
        self.img_pixels = cv2.imread(self.filename)

if __name__ == '__main__':
    filename = os.path.join(project_path, 'test_imgs', 'orientation', '2_1.jpg' )
    f1 = JPEG_metadata(filename)
    print(f1.img_pixels.size)

    filename = os.path.join(project_path, 'test_imgs', 'orientation', '2_2.jpg' )
    f2 = JPEG_metadata(filename)
    print(f2.img_pixels.size)