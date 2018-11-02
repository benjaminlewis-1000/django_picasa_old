from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.validators import *
from datetime import datetime
from django.utils import timezone

# Create your models here.

class Face(models.Model):
    # Primary key comes for free
    person_name = models.CharField(max_length=100)

class Directory(models.Model):
    dir_path = models.CharField(max_length=255)
    
class ImageFile(models.Model):
    filename = models.FilePathField(max_length=255, validators=[RegexValidator(regex="\.[j|J][p|P][e|E]?[g|G]$", message="Filename must be a JPG")])
#    filename = models.FilePathField(validators=[FileExtensionValidator(allowed_extensions=['.jpg', '.jpeg', '.JPG', '.JPEG'], message="Filename must be a JPG")])
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    # CASCADE is expected; if delete directory, delete images.
    width = models.IntegerField(validators=[MinValueValidator(1)])
    height = models.IntegerField(validators=[MinValueValidator(1)])
    # Default for date take in January 1, 1899.
    dateTaken = models.DateTimeField( default=datetime(1899, 1, 1) )
    dateTakenValid = models.BooleanField(default=False)
    # Default for date added is now.
    dateAdded = models.DateTimeField( default=timezone.now )
    isProcessed = models.BooleanField(default=False)
    orientation = models.IntegerField(default=-8008)

    # Orientation ? 
