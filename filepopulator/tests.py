from django.test import TestCase
from django.core.exceptions import ValidationError
from django import forms
from django.conf import settings
import os

# Create your tests here.

from .models import ImageFile, Directory
from .forms import ImageFileForm, DirectoryForm
from .views import create_or_get_directory, create_image_file

class ImageFileTests(TestCase):

    def setUp(self):

        self.val_img_prefix = settings.VAL_DIRECTORY # '/validation_imgs'
        self.val_train = os.path.join(self.val_img_prefix, 'train')
        self.val_test = os.path.join(self.val_img_prefix, 'test')

        assert os.path.isdir(self.val_img_prefix), 'Validation directory in ImageFileTests does not exist.'
        assert os.path.isdir(self.val_train), 'val_train directory in ImageFileTests does not exist.'
        assert os.path.isdir(self.val_test), 'val_test directory in ImageFileTests does not exist.'

        self.test_dir = os.path.join('/code', 'test_imgs', 'naming')
        self.good_dir = os.path.join(self.test_dir, 'good')
        self.bad_dir = os.path.join(self.test_dir, 'bad')

        self.goodFiles = []
        self.badFiles = []

        for root, dirs, files in os.walk(self.good_dir):
            for fname in files:
                self.goodFiles.append(os.path.join(root, fname) )

        # List of files that exist but that don't meet the file extension properties.
        for root, dirs, files in os.walk(self.bad_dir):
            for fname in files:
                self.badFiles.append(os.path.join(root, fname) )
            
        # Add files that don't exist.
        self.badFiles.append(os.path.join(self.val_img_prefix, 'asdf.png'))
        self.badFiles.append(os.path.join('aaa', 'a.png'))
        self.badFiles.append(os.path.join('/images2', 'b.jpg'))
        self.badFiles.append(os.path.join('aaa', 'a.jpg'))

    def test_dir_create(self):
        key = create_or_get_directory(self.val_train)
        key2 = create_or_get_directory(self.val_train)
        key3 = create_or_get_directory(self.val_test)
        self.assertIs(key == key2, True)
        self.assertIs(key == key3, False)

    def test_file_names(self):
        
        for good in self.goodFiles:
            create_image_file(good) #, -3, 3, self.dir_prefix)

        for bad in self.badFiles:
            try:
                create_image_file(bad) #, 3, 3, self.dir_prefix)
            except:
                # Should get this - do nothing here
                pass
#            self.assertIs( ImageFile.objects.filter(filename = bad).count(), 0)

        allObjects = ImageFile.objects.all()
        allFiles = []
        for num in range(len(allObjects) ):
            # Double check that all files in the good directory are in the database.
            # filename = allObjects[num].filename
            # directory = allObjects[num].directory
            # expand_dir = directory.dir_path 
            # print(directory.dir_path)
            fullname = allObjects[num].filename
            allFiles.append(fullname)
            # print("Object in database is : " + fullname)
            # self.assertIs( allObjects[num].dateTakenValid, True )

        for eachGood in self.goodFiles:
            # print(eachGood)
            self.assertIs(eachGood in allFiles, True, 'File {} has a name that is valid but Django thinks is not.'.format(eachGood) )

        for eachBad in self.badFiles:
            # print(eachBad)
            self.assertIs(eachBad in allFiles, False, 'File {} has a name that Django thinks is valid but is not.'.format(eachGood))

        # Clean up the thumbnails
        for obj in allObjects:
            obj.thumbnail.delete()
            obj.delete()

    def test_multiple_inputs(self):
        goodFile = self.goodFiles[0]
        create_image_file(goodFile)
        create_image_file(goodFile)
        print(goodFile)
        print(ImageFile.objects.filter(filename = goodFile).count())

    def test_imfile_create(self):


#            create_image_file(good, 30, 30, self.dir_prefix)
#            self.assertIs( ImageFile.objects.filter(filename = good).count(), 1)

        print(ImageFile.objects.all())



