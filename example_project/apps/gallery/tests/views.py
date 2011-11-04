
from django.core.urlresolvers import reverse

from django.test import TestCase

class GalleryViewTest(TestCase):

    def setUp(self):
        pass
    
    def test_gallery_list_template(self):
        url = reverse("gallery_list")
        response = self.client.get(url)

        self.assertTemplateUsed(response, "gallery/gallery_list.html")
