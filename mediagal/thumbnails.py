"""
==========
Thumbnails
==========

Interface for kicking off thumbnail generation.
"""

from mediagal import settings as gallery_settings
from mediagal.tasks import generate_thumbnail


def generate_all_thumbnails(image):
    """
    Takes a :class:`mimesis.models.MediaUpload` object and starts tasks to generate it's thumbnails.
    """
    for size_name, ratio in gallery_settings.THUMBNAIL_SIZES.items():
        generate_thumbnail.delay(image, ratio)
