#! /usr/bin/env python

# Face tagging test

import os
import face_recognition
from PIL import Image
from time import sleep
import cv2
import pyexiv2
from pyPicasaFaceXMP import picasaXMPFaceReader as pfr
from rectangle import Rectangle as rec

train_dir = '/home/benjamin/Desktop/photos_for_test/train'
test_dir = '/home/benjamin/Desktop/photos_for_test/test'

for root, dirs, files in os.walk(train_dir):
    for name in files:
        fullPath = os.path.join(root, name)
        print fullPath

        metadata = pyexiv2.ImageMetadata(fullPath)
        metadata.read()
        picasaMetadata = pfr.Imagedata(fullPath)
        xmpFaces = pfr.XMPFace(picasaMetadata).getFaces()
        # print xmpFaces

        # # Load as a numpy array
        image = face_recognition.load_image_file(fullPath)
        ocvImage = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # ocvImage = cv2.resize(ocvImage, (800, 600) )
        for faces in xmpFaces:
            personName = faces[4]

            left = faces[0]
            top = faces[1]
            width = faces[2]
            height = faces[3]
            right = left + width
            bottom = top + height
            locRect = rec(left, top, right, bottom)

            cv2.rectangle(ocvImage, (left, top), (right, bottom), (255, 0, 0), 5)
        # print ocvImage.shape

        # print image.shape
        ocvImage = cv2.resize(ocvImage, ( ocvImage.shape[1] / 10, ocvImage.shape[0] / 10 ) )
        print ocvImage.shape
        face_locations = face_recognition.face_locations(ocvImage, number_of_times_to_upsample=3,  model='cnn')
        # print face_locations

        for location in face_locations:
            top, right, bottom, left = location
            locRect = rec(left, top, right, bottom)
            face_image = image[top:bottom, left:right]
            cv2.rectangle(ocvImage, (left, top), (right, bottom), (0, 255, 0), 5)
            # pil_image = Image.fromarray(face_image)
            # pil_image.show()



        # Convert to OpenCV colors, get a resized window, and show image. 
        cv2.namedWindow('Resized Window', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Resized Window', 800, 600)
        cv2.imshow('Resized Window', ocvImage)
        cv2.waitKey(0)
        # sleep(1)
        # cv2.destroyAllWindows()

            # sleep(0.3)
            # pil_image.close()