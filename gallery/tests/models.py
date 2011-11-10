from os.path import abspath, basename, join, exists
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
        
        
    def test_deleting_gallery(self):
        g = Gallery.objects.create(name="My gallery", owner=self.user)
        
        image = MediaUpload.objects.create(caption="", media=self.test_file, creator=self.user)
        
        test_id= image.id
        
        g.add_media(image)
        
        g.delete()
        
        self.assertRaises(MediaUpload.objects.get, id=test_id)
        
        self.assertFalse(Gallery.objects.all())
        
        
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
        
    def test_remove_media(self):
        im = MediaUpload(caption="", media=self.test_file, creator=self.user)
        im.save()
        
        self.g.add_media(im)
        
        self.assertTrue(im in self.g.media.all())
        
        self.g.remove_media(im)
        
        self.assertTrue(im not in self.g.media.all())
        
        
class TestZips(TestModelsBase):
    
    def setUp(self):
        super(TestZips, self).setUp()
        self.zip = join(django_settings.MEDIA_ROOT, "test.zip")
        self.g = Gallery(name="test gallery", owner=self.user)
        self.g.save()
        
    def test_creating_from_zip(self):
        self.g.from_zip(self.zip, initial=True)
        
        all_gallery_media = GalleryMedia.objects.all()
        
        self.assertEqual(5, len(all_gallery_media))
        
        for gallery_media in all_gallery_media:
            self.assertEqual(self.g, gallery_media.gallery)
            
        self.assertEqual("test1.jpg", basename(self.g.cover.media.name))
        
    def test_adding_from_zip(self):
        self.g.from_zip(self.zip)
        
        all_media = self.g.media.all()
        
        self.assertEqual(5, len(all_media))
        
        self.assertFalse(self.g.cover)
        
