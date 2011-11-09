from os.path import abspath, join, exists
from shutil import rmtree

from django.test import TestCase

from django.core.files import File
from django.conf import settings as django_settings

from django.contrib.auth.models import User

from mimesis.models import MediaUpload

from gallery.models import Gallery, GalleryMedia



class TestModels(TestCase):
    
    def setUp(self):
        self.user = User(username="tester", password="test")
        self.user.save()
        
        self.test_file = File(open(join(django_settings.MEDIA_ROOT, "test.jpg")))

    def tearDown(self):
        self.test_file.close()
        
        mimesis_root = abspath(join(django_settings.MEDIA_ROOT, "mimesis"))
        if exists(mimesis_root):
            rmtree(mimesis_root)
            
    def test_creating_gallery(self):
        g = Gallery(name="My gallery", owner=self.user)
        self.assertEqual("My gallery", g.name)
        
    def test_adding_media(self):
        g = Gallery(name="test gallery", owner=self.user)
        g.save()
        
        image = MediaUpload(caption="", media=self.test_file, creator=self.user)
        image.save()

        g.add_media(image)
        
        self.assertTrue(image in g.media.all())
        
    def test_adding_multiple_media(self):
        g = Gallery(name="test gallery", owner=self.user)
        g.save()
        
        im1 = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im1.save()
        im2 = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im2.save()
        im3 = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im3.save()
        
        g.add_media(im1)
        g.add_media(im2)
        g.add_media(im3)
        
        all_media = g.media.all()
        
        self.assertTrue(im1 in all_media)
        self.assertTrue(im2 in all_media)
        self.assertTrue(im3 in all_media)
