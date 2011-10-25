"""
==========
Thumbnails
==========

Interface for kicking off thumbnail generation.
"""

import os

from apps.gallery import settings as gallery_settings
from apps.gallery.tasks import generate_thumbnail

def _make_out_path(image, size_name):
    """
    Generates an output file name for thumbnails.

    The output path for each thumbnail is formatted as follows::
    
        <original_filename>_<size_name>.<original_extension>
    
    """
    filename = os.path.basename(image.path)
    filename, ext = os.path.splitext(filename)
    
    out_filename = "%s%s" % ("_".join([filename, size_name]), ext)
    
    return os.path.join(gallery_settings.THUMBNAIL_ROOT, out_filename)


def generate_all_thumbnails(image):
    """
    Takes a :class:`mimesis.models.MediaUpload` object and starts tasks to generate it's thumbnails.
    """
    print "Generating thumbnails"
    for size_name, ratio in gallery_settings.THUMBNAIL_SIZES.items():
        # We only want the filename here, not the whole path it's saved at.
        
        out_path = _make_out_path(image, size_name)
        
        print "Calling with args: %s, %s" % (image, size_name)

        generate_thumbnail.delay(image, ratio, out_path)
