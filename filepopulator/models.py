from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.validators import *

# Create your models here.

class Face(models.Model):
    # Primary key comes for free
    person_name = models.CharField(max_length=100)

class Directory(models.Model):
    dir_path = models.CharField(max_length=255)
    
class ImageFile(models.Model):
    filename = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY, match="\.[j|J][p|P][e|E]*[g|G]$", max_length=255, validators=[RegexValidator(regex="\.[j|J][p|P][e|E]*[g|G]$", message="Filename must be a JPG")])
#    filename = models.FilePathField(validators=[FileExtensionValidator(allowed_extensions=['.jpg', '.jpeg', '.JPG', '.JPEG'], message="Filename must be a JPG")])
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    # CASCADE is expected; if delete directory, delete images.
    width = models.IntegerField(validators=[MinValueValidator(1)])
    height = models.IntegerField(validators=[MinValueValidator(1)])

# class ImageFileForm(ModelForm):
#     class Meta:
#         model = ImageFile
#         fields = ['filename', 'directory', 'width', 'height']
#     
# class DirectoryForm(ModelForm):
#     class Meta:
#         model = Directory
#         fields = ['dir_path']
