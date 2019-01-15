#! /usr/bin/env python

import cognitive_face as cf # Python cognitive face
from io import BytesIO
from PIL import Image, ImageDraw
import re
import rectangle
import math
import cv2 as cv

key = '998beed453094ff783a7bf72c53a7d17'

BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/'  # Replace with your regional Base URL
cf.BaseUrl.set(BASE_URL)

cf.Key.set(key)

img_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
result = cf.face.detect(img_url)
print result

one_img = '/home/lewis/test_imgs/DSC_9833.JPG'

cv_img = cv.imread(one_img)

import pyexiv2
metadata = pyexiv2.ImageMetadata(one_img)
metadata.read()

xmp = metadata.xmp_keys

regionlist_bases = re.compile('.*RegionList\[\d+\]$')
regionKeys = filter(regionlist_bases.match, xmp)

# names = [metadata[key].value for key in nameKeys]

namekey = '/mwg-rs:Name'
typekey = '/mwg-rs:Type'
areakey ='/mwg-rs:Area'
xkey = '/mwg-rs:Area/stArea:x'
ykey = '/mwg-rs:Area/stArea:y'
widthkey = '/mwg-rs:Area/stArea:w'
heightkey = '/mwg-rs:Area/stArea:h'
# '/mwg-rs:Area/stArea:unit'


photoWidth = metadata['Exif.Photo.PixelXDimension'].value
photoHeight = metadata['Exif.Photo.PixelYDimension'].value
for base in regionKeys:
    personName = metadata[base + namekey].value
    whatis = metadata[base + typekey].value
    # area = metadata[base + areakey]
    x = int(math.floor(float(metadata[base + xkey].value) * photoWidth))
    y = int(math.floor(float(metadata[base + ykey].value) * photoHeight))
    width = int(math.floor(float(metadata[base + widthkey].value) * photoWidth))
    height = int(math.floor(float(metadata[base + heightkey].value) * photoHeight))

    print personName, x, y, width, height

    rec = rectangle.Rectangle(height, width, centerX=x, centerY=y )

    # rec.drawOnPhoto(cv_img)

    roi = rec.chipFace(cv_img)

    firstname = personName.split(' ')
    firstname = firstname[0]
    cv.imwrite('/tmp/'+ firstname + '.jpg', roi)


cv_img = cv.resize(cv_img, (cv_img.shape[1] / 6, cv_img.shape[0]/ 6))
cv.imshow('cv_img',cv_img)
cv.waitKey(0)

# print nameKeys
# print names





