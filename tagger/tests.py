from django.test import TestCase
from django.core.exceptions import ValidationError
from django import forms
import os

# Create your tests here.

from .models import ImageFile, Directory
from .forms import ImageFileForm, DirectoryForm
from .views import create_directory, create_image_file

class ImageFileTests(TestCase):

    def setUp(self):
        self.dir_prefix = '/images'
        width = 100
        height = 100
    
#        d1 = Directory(dir_path=dir_prefix) 
        d1 = DirectoryForm()
        new_dir = d1.save(commit=False)
        new_dir.dir_path = self.dir_prefix
        new_dir.save()
#        d1.save()
        dir_key = Directory.objects.get(dir_path=self.dir_prefix)
#        print(dir_key.dir_path)
#        print(dir(dir_key))



#            f1 = ImageFileForm()
#            new_file = f1.save(commit=False)
#            new_file.filename=good
#            new_file.width=width
#            new_file.height=height
#            new_file.directory=dir_key #Directory.objects.filter(dir_path==dir_prefix)
#            new_file.save()

    def test_mm(self):
        from .models import MyModel
        
        instance = MyModel(name="Some Name", size=15)
        try:
            instance.full_clean()
        except ValidationError:
            pass
            print("No pass!")
            # Do something when validation is not passing
        else:
            # Validation is ok we will save the instance
            instance.save()

    def test_dir_create(self):
        create_directory(self.dir_prefix)

    def test_imfile_create(self):
        file1 = os.path.join(self.dir_prefix, 'Pictures_finished/ben_young.jpg')
        file2 = os.path.join(self.dir_prefix, 'test2.jpeg')
        file3 = os.path.join(self.dir_prefix, 'asdf', 'bbk', 'test3.JPG')
        file4 = os.path.join(self.dir_prefix, 'asdf', 'bbk', 'test4.JPEG')

        self.goodFiles = [file1, file2, file3, file4]

        for good in self.goodFiles:
            create_image_file(good, -3, 3, self.dir_prefix)

        bad1 = os.path.join(self.dir_prefix, 'asdf.png')
        dir_key = Directory.objects.get(dir_path=self.dir_prefix)
        instance = ImageFile(filename=bad1, height=3, width=10, directory=dir_key)
        try:
            instance.full_clean()
        except ValidationError:
            pass
            print("No pass image file!")
            # Do something when validation is not passing
        else:
            # Validation is ok we will save the instance
            instance.save()

        bad2 = os.path.join('aaa', 'a.png')
        bad3 = os.path.join('/images2', 'b.jpg')
        bad4 = os.path.join('aaa', 'a.jpg')

        self.badFiles = [bad2, bad3, bad4, bad1]

        for bad in self.badFiles:
            create_image_file(bad, 3, 3, self.dir_prefix)

            try:
                test1 = ImageFile.objects.get(filename = bad)
            except:
                print("Success, test1 isn't in the table!")
#        print(test1)
        print("Done with imfile_create")

#        for bad in self.badFiles:
#
#            new_file = ImageFile() #f1.save(commit=False)
#            new_file.filename=bad
#            new_file.width=width
#            new_file.height=height
#            new_file.directory=dir_key #Directory.objects.filter(dir_path==dir_prefix)
#            f1 = ImageFileForm(instance = new_file)
#            print(f1.is_valid())
#            f1.save()
#
#    def test_check_only_jpgs_can_add(self):
#        # Check that filenames with extension of jpg, jpeg, JPG, and JPEG - only - can add.
#
#        for file in self.goodFiles:
#            try:
#                db_key = ImageFile.objects.get(filename=file)
#                print(db_key)
#                self.assertIs(True, True)
#            except ImageFile.DoesNotExist as dne:
#                self.assertIs(False, True)
#
#        for file in self.badFiles:
#            try:
#                db_key = ImageFile.objects.get(filename=file)
#                print(db_key)
#                print("Failing file: " + str(file) )
#                self.assertIs(False, True)
#            except ImageFile.DoesNotExist as dne:
#                print("Does not exist")
#                self.assertIs(True, True)
