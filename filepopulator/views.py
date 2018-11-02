from django.shortcuts import render

# Create your views here.

from .forms import ImageFileForm, DirectoryForm
from .models import ImageFile, Directory
from django.core.exceptions import ValidationError

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
        

def create_image_file(file_path, width, height, dir_path):
    dir_key = create_or_get_directory(dir_path)
    # Need to correlate directory somehow...

    instance = ImageFile(\
            filename = file_path,\
            width = width, \
            height = height, \
            directory = dir_key
        )

    print(file_path)
    try:
        instance.full_clean()
    except ValidationError as ve:
        print(ve)
    else:
        instance.save()

#    if_form = ImageFileForm(instance=if_object)
 #   if_form.full_clean()
