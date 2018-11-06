from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.validators import *
from datetime import datetime
from django.utils import timezone

from io import BytesIO
from django.core.files.base import ContentFile
import os
import time
import hashlib
import PIL
from PIL.ExifTags import TAGS 
from PIL import Image
from datetime import datetime
from django.core.files import File
import pytz
# Create your models here.

class Face(models.Model):
    # Primary key comes for free
    person_name = models.CharField(max_length=100)

class Directory(models.Model):
    dir_path = models.CharField(max_length=255)
    
# Lots ripped from https://github.com/hooram/ownphotos/blob/dev/api/models.py 
class ImageFile(models.Model):

    filename = models.CharField(max_length=255, validators=[RegexValidator(regex="\.[j|J][p|P][e|E]?[g|G]$", message="Filename must be a JPG")], db_index = True)
    # CASCADE is expected; if delete directory, delete images.
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    image_hash = models.CharField(primary_key = True, max_length = 64, null = False, default = -1)

    # Thumbnails 
    thumbnail = models.ImageField(upload_to='thumbnails')
    # thumbnail_tiny = models.ImageField(upload_to='thumbnails_tiny')
    # thumbnail_small = models.ImageField(upload_to='thumbnails_small')
    # thumbnail_big = models.ImageField(upload_to='thumbnails_big')

    # square_thumbnail = models.ImageField(upload_to='square_thumbnails')
    # square_thumbnail_tiny = models.ImageField(
    #     upload_to='square_thumbnails_tiny')
    # square_thumbnail_small = models.ImageField(
    #     upload_to='square_thumbnails_small')
    # square_thumbnail_big = models.ImageField(upload_to='square_thumbnails_big')


    dateAdded = models.DateTimeField( default=timezone.now )
    width = models.IntegerField(validators=[MinValueValidator(1)])
    height = models.IntegerField(validators=[MinValueValidator(1)])

    # Default for date take in January 1, 1899.
    dateTaken = models.DateTimeField( default=datetime(1899, 1, 1) )
    dateTakenValid = models.BooleanField(default=False)

    # Default for date added is now.
    isProcessed = models.BooleanField(default=False)
    orientation = models.IntegerField(default=-8008)
    # thumbnail = models.ImageField(upload_to = settings.THUMBNAIL_DIR, default = str(timezone.now) + '_thumbnail.jpg' )

    def _get_full_path(self):
        expand_dir = self.directory.dir_path
        fullname = os.path.join(expand_dir, self.filename)
        return fullname

    # def _split_full_path_to_file_and_dir(self):
    #     tmp_filepath = self.filename
    #     self.filename = os.path.basename(os.path.normpath( tmp_filepath ) )
    #     directory_of_file = os.path.dirname( os.path.normpath( tmp_filepath ) )
    #     dir_key = create_or_get_directory(directory_of_file)


    def _process_new(self):
        # try:
        #     self.full_clean()
        # except ValidationError as ve:
        #     print(ve)
        # else:
        self._init_image()
        self._generate_md5_hash()
        self._generate_thumbnail()
        self._get_date_taken()

    def _init_image(self):
        self.full_path = os.path.join(self.directory.dir_path, self.filename)
        self.image = PIL.Image.open(self.full_path)
        self.exifDict = {}
        info = self.image._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            self.exifDict[decoded] = value
        self.isProcessed = False
        self.orientation = self.exifDict['Orientation']
        self.dateAdded = timezone.now()

    # Orientation ? 
    def _generate_md5_hash(self):
        hash_md5 = hashlib.md5()
        # self.full_path = os.path.join(directory.dir_path, filename)
        with open(self.full_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        hash_md5.update(str(time.time()).encode('utf-8'))
        self.image_hash = hash_md5.hexdigest() 
        # print(self.image_hash)

    def _get_date_taken(self):
        # Default comparison date - we want the earliest date.
        self.dateTaken = timezone.now()
        # Flag for if we found a date taken in the EXIF data. 
        self.dateTakenValid = False
        dateTakenKeys = ['DateTimeOriginal', 'DateTimeDigitized']
        for exifKey in dateTakenKeys:
            datetaken_tmp = self.exifDict[exifKey]
            if datetaken_tmp is None:
                continue  # No value at this EXIF key
            else:
                date = datetime.strptime(datetaken_tmp, '%Y:%m:%d %H:%M:%S')
                date = pytz.utc.localize(date)
                if date < self.dateTaken: 
                    self.dateTaken = date
                    self.dateTakenValid = True

        # Make the taken date timezone aware to get rid of warnings.
        # self.dateTaken = (self.dateTaken)

    def _generate_thumbnail(self):
        # PIL will open the image without regard to the orientation flag. So we need to open it and get the
        # data for the orientation, then orient correctly before deciding on width and height. 

        # full_path = os.path.join(self.directory.dir_path, self.filename)

        # If no ExifTags, no rotating needed.
        try:
            # Grab orientation value.
            # Already done in _init_image()

            # Rotate depending on orientation.
            if self.orientation == 2:
                self.image = self.image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            if self.orientation == 3:
                self.image = self.image.transpose(PIL.Image.ROTATE_180)
            if self.orientation == 4:
                self.image = self.image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            if self.orientation == 5:
                self.image = self.image.transpose(PIL.Image.FLIP_LEFT_RIGHT).transpose(
                    PIL.Image.ROTATE_90)
            if self.orientation == 6:
                self.image = self.image.transpose(PIL.Image.ROTATE_270)
            if self.orientation == 7:
                self.image = self.image.transpose(PIL.Image.FLIP_TOP_BOTTOM).transpose(
                    PIL.Image.ROTATE_90)
            if self.orientation == 8:
                self.image = self.image.transpose(PIL.Image.ROTATE_90)
        except:
            # Orientation 1 
            pass

        self.width, self.height = self.image.size

        self.image.thumbnail(settings.THUMBNAIL_SIZE_BIG,
                        PIL.Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        # self.image.save(image_io_thumb, format="JPEG")
        self.thumbnail = ContentFile(image_io_thumb.getvalue())
        self.thumbnail.name = self.image_hash + '.jpg'

        image_io_thumb.close()