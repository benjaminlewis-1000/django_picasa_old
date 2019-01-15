#! /usr/bin/env python

from pyPicasaFaceXMP import picasaXMPFaceReader as pfr

testFile = '/tmp/copyfile.jpg'

metadata = pfr.Imagedata(testFile)

xmpface = pfr.XMPFace(metadata)
print xmpface.getFaces()

tlx = 2700
tly = 800
wid = 900
hei = 1080
xmpface.setDim(6000, 4000)
index = len(xmpface.getFaces()) 
faces = xmpface.getFaces()
print faces[0]
xmpface.setFace(tlx, tly, wid, hei, "Phantom buddy #{}".format(index), index=index)
xmpface.save_file(testFile)