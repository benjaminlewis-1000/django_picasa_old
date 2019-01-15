#! /usr/bin/env python

import cv2 as cv
import pyexiv2
from PIL import Image, ExifTags
import math
import os
import re
import warnings
from rectangle import Rectangle
import xmltodict
import hashlib
from pyPicasaFaceXMP import picasaXMPFaceReader as pfr
from cnnFaceExtract import imageFaceDetect
import time

path_to_script = os.path.dirname(os.path.realpath(__file__))

# pyexiv2.xmp.register_namespace('http://example.org/foo/', 'foo')
# md['Xmp.foo.one'].value

class photo():

    def __init__(self, imageFilePath, xmlParamsFile):

        with open(xmlParamsFile) as stream:
            try:
                self.params = xmltodict.parse(stream.read())
                self.params = self.params['parameters']
            except Exception as exc:
                print(exc)
                exit(1)

        self.READ_INTO_DB = 1
        self.SENT_TO_MSFT = 2
        self.ALL_FACES_TAGGED = 4

        m = hashlib.md5()
        m.update(imageFilePath)
        self.pathHash = m.hexdigest()

        # OpenCV seems to take orientation metadata into account by default.
        # We don't have to use this to load the image, but it may be useful to 
        # put the region tags. 
        try:

            self.metadata = pyexiv2.ImageMetadata(imageFilePath)
            self.metadata.read()
            self.orientation = self.metadata.__getitem__("Exif.Image.Orientation").value

        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            self.orientation = 1
            pass

        self.picasaMetadata = pfr.Imagedata(imageFilePath)
        self.xmpFaces = pfr.XMPFace(self.picasaMetadata)
        # print imageFilePath, self.orientation

        try:
            self.cvImg = cv.imread(imageFilePath)
            self.grayscale = cv.cvtColor(self.cvImg, cv.COLOR_BGR2GRAY)
        except (AttributeError, KeyError, IndexError):
            # cases: imagedon't have getexif
            pass
        self.photoHeight, self.photoWidth, channels = self.cvImg.shape

        # Hash the top-left 100 x 100 pixels (or whole image if smaller)
        # to determine the orientation of the image and whether the image has changed.
        orientHash = hashlib.md5()
        if self.cvImg.shape >= (100, 100):
            smallArray = self.cvImg[0:100, 0:100]
        else:
            smallArray = self.cvImg

        # Prevent a C-contiguous order error
        smallArray = smallArray.copy(order='C')
        orientHash.update(smallArray)
        self.orientationHash = orientHash.hexdigest()
        # print self.orientationHash


        # # Define the sub-keys for the areas of interest in the metadata
        # # which store face attributes. 
        # self.namekey = '/mwg-rs:Name'
        # self.typekey = '/mwg-rs:Type'
        # self.areakey ='/mwg-rs:Area'
        # self.xkey = '/mwg-rs:Area/stArea:x'
        # self.ykey = '/mwg-rs:Area/stArea:y'
        # self.widthkey = '/mwg-rs:Area/stArea:w'
        # self.heightkey = '/mwg-rs:Area/stArea:h'

        self.extract_stored_faces()

    def extract_stored_faces(self):

        faces = self.xmpFaces.getFaces()

        self.faces = []
        
        for i in range(len(faces)):
            personName = faces[i][4]

            left = faces[i][0]
            top = faces[i][1]
            width = faces[i][2]
            height = faces[i][3]

            rect = Rectangle(height=height, width=width, leftEdge = left, topEdge = top)
            # Extract the pixels of the face
            roi = self.chipFace(rect)

            returnDict = dict()
            returnDict['name'] = personName
            returnDict['rectangle'] = rect
            returnDict['chip_image'] = roi

            # Put the person's name, the rectangle, and the roi image
            # into a tuple and append to the faces array.
            self.faces.append( returnDict )

        return self.faces

    def faceClassify(self):
        locPlusEmbed = imageFaceDetect(self.cvImg)
        for rect, embed in locPlusEmbed:
            for faceDict in self.faces:
                storedFace = faceDict['rectangle']
                intersection = rect.intersect(storedFace)
                print intersection['r1_percent']
                print intersection['r2_percent']

    def chipFace(self, rectangle):
        # print self.top, self.height, self.left, self.width
        top = rectangle.top
        height = rectangle.height
        left = rectangle.left
        width = rectangle.width
        roi = self.cvImg[top:top+height, left:left+width]
        return roi

    def tagFace(self, rectangle, name, cvImg):
        pass
        # Check if the rectangle is normalized or not.
        newFaceNum = len(self.faces) + 1 # Face index is 1-indexed in this case.  
        centerX = rectangle.centerX
        centerY = rectangle.centerY
        height = rectangle.height
        width = rectangle.width
        if height > 1:
            centerX = float(centerX) / self.photoWidth 
            centerY = float(centerY) / self.photoHeight
            width = width / self.photoWidth
            height = height / self.photoHeight


    def get_state_tags(self):
        pass

if __name__ == "__main__":

    xmlParamsFile = os.path.join(path_to_script, 'params.xml')

    def unitTest(path):
        pht = photo(path, xmlParamsFile) 
        cvImg = cv.imread(path)
        faces = pht.extract_stored_faces()
        for i in range(len(faces)):
            rect = faces[i]['rectangle']
            rect.drawOnPhoto(cvImg, colorTriple=(0,255,0))

        cv.namedWindow('dst_rt', cv.WINDOW_NORMAL)
        cv.resizeWindow('dst_rt', 400, 500)

        cv.imshow('dst_rt', cvImg)
        cv.waitKey(0)
        cv.destroyAllWindows()

    unitTest('/home/lewis/test_imgs/DSC_9837.JPG')

    unitTest('/home/lewis/test_imgs/2018-03-24 11.28.48-2.jpeg')

    unitTest('/home/lewis/test_imgs/DSC_9836.JPG')

    unitTest('/home/lewis/test_imgs/DSC_9858.JPG')

    pht = photo('/home/lewis/test_imgs/2018-03-24 11.28.48-2.jpeg', xmlParamsFile)
    pht.faceClassify()



    # for root, dirname, file in os.walk('/home/lewis/test_imgs', topdown=False):
    #     # print file[0]
    #     # print dirname
    #     for fname in file:
    #         this_img = photo(os.path.join(root, fname), xmlParamsFile)
    #         this_img.detect_faces()
    # # photo(path)


      # def detect_faces(self):
    #     front_cascade = cv.CascadeClassifier(os.path.join(path_to_script, 'haar.xml'))
    #     side_cascade = cv.CascadeClassifier(os.path.join(path_to_script, 'haarside.xml'))
    #     lpb_cascade  = cv.CascadeClassifier(os.path.join(path_to_script, 'lpb_cascade.xml'))

    #     image_size = self.cv_img.shape

    #     min_face_downscale = int(self.params['minFaceSizeScale'])
    #     print min_face_downscale
    #     min_width = image_size[0] / min_face_downscale
    #     min_height = image_size[1] / min_face_downscale

    #     minSize = ( min_width, min_height )

    #     warnings.warn('Cascade classifiers have not been tuned yet.')
    #     faces = front_cascade.detectMultiScale(self.grayscale, \
    #         float(self.params['frontScaleFactor']), int(self.params['frontMinNeighbors']), \
    #         minSize = minSize)
    #     faces_side = side_cascade.detectMultiScale(self.grayscale, \
    #         float(self.params['sideScaleFactor']), int(self.params['sideMinNeighbors']), \
    #         minSize = minSize)

    #     flipImg = cv.flip(self.grayscale,0)

    #     faces_side2 = lpb_cascade.detectMultiScale(self.grayscale, \
    #         float(self.params['sideScaleFactor']), int(self.params['sideMinNeighbors']), \
    #         minSize = minSize)
    #     faces_side3 = lpb_cascade.detectMultiScale(flipImg, \
    #         float(self.params['sideScaleFactor']), int(self.params['sideMinNeighbors']), \
    #         minSize = minSize)

    #     self.face_rect_array = []

    #     num_faces = 0


    #     for (x,y,w,h) in faces:
    #         num_faces += 1
    #         faceRect = Rectangle(h, w, topLeftX=x, topLeftY=y)
    #         # cv.rectangle(self.cv_img,(x,y),(x+w,y+h),(0,255,0),8)
    #         faceRect.drawOnPhoto(self.cv_img)
    #         self.face_rect_array.append(faceRect)

    #     for (x,y,w,h) in faces_side:
    #         num_faces += 1
    #         faceRect = Rectangle(h, w, topLeftX=x, topLeftY=y)
    #         faceRect.drawOnPhoto(self.cv_img, colorTriple=(255,255,0))
    #         # cv.rectangle(self.cv_img,(x,y),(x+w,y+h),(255,0,0),8)
    #         self.face_rect_array.append(faceRect)

    #     for (x,y,w,h) in faces_side2:
    #         num_faces += 1
    #         faceRect = Rectangle(h, w, topLeftX=x, topLeftY=y)
    #         faceRect.drawOnPhoto(self.cv_img, colorTriple=(0,255,140))
    #         # cv.rectangle(self.cv_img,(x,y),(x+w,y+h),(255,0,0),8)
    #         self.face_rect_array.append(faceRect)

    #     for (x,y,w,h) in faces_side3:
    #         num_faces += 1
    #         faceRect = Rectangle(h, w, topLeftX=x, topLeftY=y)
    #         faceRect.drawOnPhoto(self.cv_img, colorTriple=(0,0,255))
    #         # cv.rectangle(self.cv_img,(x,y),(x+w,y+h),(255,0,0),8)
    #         self.face_rect_array.append(faceRect)

    #     if len(self.face_rect_array) >= 2:
    #         print self.face_rect_array[0].intersect(self.face_rect_array[1])

    #     self.cv_img = cv.resize(self.cv_img, (self.cv_img.shape[1] / 6, self.cv_img.shape[0]/ 6))
    #     cv.imshow('cv_img',self.cv_img)
    #     cv.waitKey(0)

    #     print "Number of faces found: " + str(num_faces)