from django.shortcuts import render

# Create your views here.

from .forms import ImageFileForm, DirectoryForm
from .models import ImageFile, Directory
from django.core.exceptions import ValidationError
from datetime import datetime
from django.conf import settings
from PIL import Image
from PIL.ExifTags import TAGS 
from django.core.files.base import ContentFile
from django.utils import timezone

import os

# def get_exif(img):
#     ret = {}
#     i = Image.open(img)
#     info = i._getexif()
#     for tag, value in info.items():
#         decoded = TAGS.get(tag, tag)
#         ret[decoded] = value
#     return ret

def create_or_get_directory(dir_path):
#    return Directory.objects.create(dir_path = directory_path)
    try:
        dir_key = Directory.objects.get (dir_path = dir_path)
    except :
    
        instance = Directory(dir_path = dir_path)

        try:
            instance.full_clean()
        except ValidationError as ve:
            print(ve)
        else:
            instance.save()
        dir_key = Directory.objects.get (dir_path = dir_path)

    return dir_key
        
def resize_image(PIL_img):
    width, height = PIL_img.size

    shortEdge = settings.MAX_SHORT_EDGE_THUMBNAIL
    if width > height: # Landscape
        ratio = float(width) / float(height)
        newWidth = int(ratio * shortEdge)
        newHeight = shortEdge

    else: # Portrait
        ratio = float(height) / float(width)
        newWidth = shortEdge
        newHeight = int(ratio * shortEdge)

    newSize = (newWidth, newHeight)
    thumb = PIL_img.thumbnail(newSize, Image.ANTIALIAS)
    return thumb
    

def create_image_file(file_path):

    assert os.path.isfile(file_path)
    # filename_only = os.path.basename(os.path.normpath( file_path ) )
    # directory_of_file = os.path.dirname( os.path.normpath( file_path ) )
    # dir_key = create_or_get_directory(directory_of_file)

    photo = ImageFile(filename = file_path) #
    photo.process_new()
    # Need to correlate directory somehow...

    # image = Image.open(file_path)
    # width, height = image.size
    # exif_data = get_exif(file_path)
    # current_orientation = exif_data['Orientation']
    # assert current_orientation is not None

    # # Check if this image is already in the database
    # updating = False
    # any_matches = ImageFile.objects.filter(filename = file_path, directory = dir_key)
    # if any_matches.count() > 0:
    #     # Check to see if the orientation has changed. 
    #     old_orientation = any_matches[0].orientation
    #     if old_orientation == current_orientation:
    #         return
    #     else:
    #     # else, continue on and update.
    #         updating = True
        

    # # Get the date taken:
    # # Source for these EXIF tag attributes: 
    # # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html
    # # exifDict = {}
    # # exifDict['DateTimeOriginal'] = 36867
    # # exifDict['DateTimeDigitized'] = 36868
    
    # # Source for this code snippet: 
    # # https://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
    # # Uses PIL to get a named dictionary of EXIF metadata.


    # # Default comparison date - we want the earliest date.
    # datetaken = datetime.now()
    # # Flag for if we found a date taken in the EXIF data. 
    # validDateTaken = False
    # dateTakenKeys = ['DateTimeOriginal', 'DateTimeDigitized']
    # for exifKey in dateTakenKeys:
    #     datetaken_tmp = exif_data[exifKey]
    #     if datetaken_tmp is None:
    #         continue  # No value at this EXIF key
    #     else:
    #         date = datetime.strptime(datetaken_tmp, '%Y:%m:%d %H:%M:%S')
    #         if date < datetaken: 
    #             datetaken = date
    #             validDateTaken = True

    # thumbnail = resize_image(image)

    # instance = ImageFile(
    #         filename = file_path,
    #         directory = dir_key,
    #         width = width, 
    #         height = height, 
    #         dateTaken = datetaken,
    #         dateTakenValid = validDateTaken,
    #         dateAdded = timezone.now(),
    #         isProcessed = False,
    #         orientation = current_orientation,
    #         thumbnail = thumbnail, 
    #     )

    # instance.thumbnail.save(str(timezone.now() ) + '_thumbnail.jpg', ContentFile(image) )

    try:
        photo.full_clean()
    except ValidationError as ve:
        pass
        # print(ve)
        print("Did not add photo " + file_path)
    else:
        photo.save()

        print("added photo " + file_path)

#    if_form = ImageFileForm(instance=if_object)
 #   if_form.full_clean()
