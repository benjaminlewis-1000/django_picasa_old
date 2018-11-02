from django.test import TestCase
from django.core.exceptions import ValidationError
from django import forms
import os

# Create your tests here.

from .models import ImageFile, Directory
from .forms import ImageFileForm, DirectoryForm
from .views import create_or_get_directory, create_image_file

class ImageFileTests(TestCase):

    def setUp(self):
        self.dir_prefix = '/images'
        self.dir_key = create_or_get_directory(self.dir_prefix)
        print(self.dir_key)

        file1 = os.path.join(self.dir_prefix, 'Pictures_finished/ben_young.jpg')
        file2 = os.path.join(self.dir_prefix, 'test2.jpeg')
        file3 = os.path.join(self.dir_prefix, 'asdf', 'bbk', 'test3.JPG')
        file4 = os.path.join(self.dir_prefix, 'asdf', 'bbk', 'test4.JPEG')

        self.goodFiles = [file1, file2, file3, file4]
    
#        d1 = Directory(dir_path=dir_prefix) 
#        new_dir = d1.save(commit=False)
#        new_dir.dir_path = self.dir_prefix
#        new_dir.save()
#        d1.save()
#        dir_key = Directory.objects.get(dir_path=self.dir_prefix)
#        print(dir_key.dir_path)
#        print(dir(dir_key))
        bad1 = os.path.join(self.dir_prefix, 'asdf.png')
        bad2 = os.path.join('aaa', 'a.png')
        bad3 = os.path.join('/images2', 'b.jpg')
        bad4 = os.path.join('aaa', 'a.jpg')

        self.badFiles = [bad2, bad3, bad4, bad1]



#            f1 = ImageFileForm()
#            new_file = f1.save(commit=False)
#            new_file.filename=good
#            new_file.width=width
#            new_file.height=height
#            new_file.directory=dir_key #Directory.objects.filter(dir_path==dir_prefix)
#            new_file.save()

    def test_dir_create(self):
        key = create_or_get_directory(self.dir_prefix)
        key2 = create_or_get_directory(self.dir_prefix)
        self.assertIs(key == key2, True)

    def test_imfile_create(self):

        for good in self.goodFiles:
            create_image_file(good, -3, 3, self.dir_prefix)
            self.assertIs( ImageFile.objects.filter(filename = good).count(), 0)

            create_image_file(good, 30, 30, self.dir_prefix)
            self.assertIs( ImageFile.objects.filter(filename = good).count(), 1)

        print(ImageFile.objects.all())

        for bad in self.badFiles:
            create_image_file(bad, 3, 3, self.dir_prefix)
            print(ImageFile.objects.all())
           # try:
           #     test1 = ImageFile.objects.get(filename = bad)
           #     self.assertIs(True, False)
           # except:
           #     self.assertIs(False, False)
            self.assertIs( ImageFile.objects.filter(filename = bad).count(), 0)


