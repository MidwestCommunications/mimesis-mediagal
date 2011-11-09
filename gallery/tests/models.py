from os.path import abspath, join, exists
from shutil import rmtree

from django.test import TestCase

from django.core.files import File
from django.conf import settings as django_settings

from django.contrib.auth.models import User

from mimesis.models import MediaUpload

from gallery.models import Gallery, GalleryMedia



class TestModelsBase(TestCase):
    
    def setUp(self):
        self.user = User(username="tester", password="test")
        self.user.save()
        
        self.test_file = File(open(join(django_settings.MEDIA_ROOT, "test.jpg")))

    def tearDown(self):
        self.test_file.close()
        
        mimesis_root = abspath(join(django_settings.MEDIA_ROOT, "mimesis"))
        if exists(mimesis_root):
            rmtree(mimesis_root)

class TestCreatingGallery(TestModelsBase):
            
    def test_creating_gallery(self):
        g = Gallery(name="My gallery", owner=self.user)
        self.assertEqual("My gallery", g.name)
        
class TestAddingMedia(TestModelsBase):
    
    def setUp(self):
        super(TestAddingMedia, self).setUp()
        self.g = Gallery(name="test gallery", owner=self.user)
        self.g.save()
        
    def test_adding_media(self):
        image = MediaUpload(caption="", media=self.test_file, creator=self.user)
        image.save()

        self.g.add_media(image)
        
        self.assertTrue(image in self.g.media.all())
        
    def test_adding_multiple_media(self):
        im1 = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im1.save()
        im2 = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im2.save()
        im3 = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im3.save()
        
        self.g.add_media(im1)
        self.g.add_media(im2)
        self.g.add_media(im3)
        
        all_media = self.g.media.all()
        
        self.assertTrue(im1 in all_media)
        self.assertTrue(im2 in all_media)
        self.assertTrue(im3 in all_media)
        
