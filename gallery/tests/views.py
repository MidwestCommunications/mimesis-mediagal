from os.path import join

from django.conf import settings as django_settings
from django.core.files import File
from django.core.urlresolvers import reverse

from django.test import TestCase

from django.contrib.auth.models import User

from mimesis.models import MediaUpload

from gallery.models import Gallery

class GalleryViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test_email@address.com", password="test")
        self.g = Gallery.objects.create(name="Test gallery", owner=self.user)
        
        test_file = File(open(join(django_settings.MEDIA_ROOT, "test.jpg")))
        self.media = MediaUpload.objects.create(caption="", media=test_file, creator=self.user)
        test_file.close()
        
        self.client.login(username="test", password="test")
        
    def test_gallery_list_template(self):
        url = reverse("gallery_list")
        response = self.client.get(url)

        self.assertTemplateUsed(response, "gallery/gallery_list.html")
        
    def test_gallery_list_context(self):
        url = reverse("gallery_list")
        response= self.client.get(url)
        
        self.assertTrue("galleries" in response.context)
        self.assertTrue("thumbnail_sizes" in response.context)
        
    def test_gallery_details_template(self):
        url = reverse("gallery_details", args=(self.g.id,))
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, "gallery/gallery_details.html")
        
    def test_gallery_details_context(self):
        url = reverse("gallery_details", args=(self.g.id,))
        response = self.client.get(url)
        
        self.assertTrue("gallery" in response.context)
        self.assertTrue("media" in response.context)
        self.assertTrue("thumbnail_sizes" in response.context)
        
    def test_gallery_create_template(self):
        url = reverse("gallery_create")
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, "gallery/gallery_create.html")
        
    def test_gallery_create_context(self):
        url = reverse("gallery_create")
        response = self.client.get(url)
        
        self.assertTrue("gallery_form" in response.context)
