from django.shortcuts import render

# Create your views here.

from .forms import ImageFileForm, DirectoryForm
from .models import ImageFile, Directory
from django.core.exceptions import ValidationError

def create_directory(directory_path):
    return Directory.objects.create(dir_path = directory_path)

def create_image_file(file_path, width, height, dir_path):
    dir_key = Directory.objects.get (dir_path = dir_path)


    instance = ImageFile(\
            filename = file_path,\
            width = width, \
            height = height, \
            directory = dir_key
        )

    try:
        instance.full_clean()
    except ValidationError as ve:
        print(ve)
    else:
        instance.save()

#    if_form = ImageFileForm(instance=if_object)
 #   if_form.full_clean()
