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
    
    def test_create_path(self):
        media = Gallery.objects.get(pk=1).media.get(pk=1)
        
        out_path = _make_out_path(media.media, "small")
        
        self.assertEqual(out_path, os.path.join(gallery_settings.THUMBNAIL_ROOT, "test_small.png"))
        
    def test_square_thumbnail(self):
        import pdb; pdb.set_trace()
        size = gallery_settings.THUMBNAIL_SIZES["small"]
        source = Gallery.objects.get(pk=1).media.get(pk=1).media
        
        thumb = square_thumbnail(source, size)
        
        size_str = "%sx%s" % gallery_settings.THUMBNAIL_SIZES["small"]
        
        self.assertTrue(size_str in thumb.name)

