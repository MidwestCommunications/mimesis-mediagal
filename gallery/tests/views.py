from os.path import abspath, dirname, join
from os import unlink

from django.conf import settings as django_settings
from django.core.files import File
from django.core.urlresolvers import reverse

from django.test import TestCase

from django.contrib.auth.models import User

from django.contrib.sites.models import Site
from mimesis.models import MediaUpload

from gallery.models import Gallery, GallerySites

class GalleryViewTest(TestCase):

            
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test_email@address.com", password="test")
        self.g = Gallery.objects.create(name="Test gallery", owner=self.user)
        self.site, c = Site.objects.get_or_create(id=django_settings.SITE_ID, defaults = {
                "name": "localhost",
                "domain": "localhost"
            }
        )
        GallerySites.objects.create(gallery=self.g, site=self.site)
        
        test_file = File(open(join(abspath(dirname(__file__)), "media", "test.jpg")))
        self.media = MediaUpload.objects.create(caption="", media=test_file, creator=self.user)
        test_file.close()
        
        self.g.add_media(self.media)
        
        
        self.client.login(username="test", password="test")
        
        
    def tearDown(self):
        unlink(abspath(join(django_settings.MEDIA_ROOT, self.media.media.name)))
            
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
        
        self.assertTemplateUsed(response, "gallery/gallery_create_edit.html")
        
        
    def test_gallery_create_context(self):
        url = reverse("gallery_create")
        response = self.client.get(url)
        
        self.assertTrue("gallery_form" in response.context)
        
        
    def test_gallery_create_functional_test(self):
        url = reverse("gallery_create")
        
        site = self.site
        name = "A new gallery"
        description = "My new test gallery."
        tags = "tag,"
        file = open(join(abspath(dirname(__file__)), "media", "test.zip"))
        
        response = self.client.post(url, {"name": name, "description": description, "photos": file, "sites": site.id, "tags": tags}, follow=True)
        
        self.assertTemplateUsed(response, "gallery/gallery_edit_metadata.html")
        
        gallery = Gallery.objects.get(name=name, description=description)
        
        media = gallery.media.all()
        
        self.assertTrue(5, len(media))

        for m in media:
            unlink(abspath(join(django_settings.MEDIA_ROOT, m.media.name)))
        
        
    def test_gallery_add_media_template(self):
        url = reverse("gallery_add_media", args=(self.g.id,))
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, "gallery/gallery_add_photo.html")
        
        
    def test_gallery_add_media_context(self):
        url = reverse("gallery_add_media", args=(self.g.id,))
        response = self.client.get(url)
        
        self.assertTrue("gallery" in response.context)
        self.assertTrue("form" in response.context)
        
        
    def test_gallery_delete_template(self):
        r = self.client.get(reverse("gallery_delete"))
        self.assertEqual(r.status_code, 400)
        
        
    def test_gallery_delete(self):
        url = reverse("gallery_delete")
        response = self.client.post(url, data={"gallery_id": self.g.id}, follow=True)
        
        self.assertTemplateUsed(response, "gallery/gallery_list.html")
        
        self.assertFalse(Gallery.objects.all())

        
    def test_gallery_edit_metadata_template(self):
        url = reverse("gallery_edit_metadata", args=(self.g.id,))
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, "gallery/gallery_edit_metadata.html")
        
        
    def test_gallery_edit_metadata_context(self):
        url = reverse("gallery_edit_metadata", args=(self.g.id,))
        response = self.client.get(url)
        
        self.assertTrue("gallery" in response.context)
        self.assertTrue("media_formset" in response.context)
        self.assertTrue("thumbnail_sizes" in response.context)
        self.assertTrue("delete_form" in response.context)
        
        
    def test_gallery_image_details_template(self):
        url = reverse("gallery_image_details", args=(self.g.id, self.media.id))
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, "gallery/gallery_image_details.html")
        
        
    def test_gallery_image_details_context(self):
        url = reverse("gallery_image_details", args=(self.g.id,self.media.id))
        response = self.client.get(url)
        
        self.assertTrue("media" in response.context)
        
