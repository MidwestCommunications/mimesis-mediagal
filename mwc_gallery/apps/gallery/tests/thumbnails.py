from django.test import TestCase

import os

from gallery.models import Gallery
import gallery.settings as gallery_settings
from gallery.tasks import square_thumbnail
from gallery.thumbnails import _make_out_path

class TestPathGeneration(TestCase):
    fixtures = ["test_data"]
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_square_thumbnail(self):
        size = gallery_settings.THUMBNAIL_SIZES["small"]
        source = Gallery.objects.get(pk=1).media.get(pk=1).media
        
        thumb = square_thumbnail(source, size)
        
        size_str = "%sx%s" % gallery_settings.THUMBNAIL_SIZES["small"]
        
        self.assertTrue(size_str in thumb.name)

