"""
====
Tasks
====

Tasks are provided for the Celery job management library that generate thumbnails for uploaded images in the background.
"""
from django.conf import settings

from celery.decorators import task

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError


@task
def generate_media_thumbnails(media_upload, *args, **kwargs):
    """
    Creates a new image of the given ratio, saving it to the provided output path.
    """
    for thumbnail_options in settings.GALLERY_THUMBNAIL_SIZES:
        thumbnailer = get_thumbnailer(media_upload.media)
        try:
        	thumbnailer.get_thumbnail(thumbnail_options)
        except InvalidImageFormatError:
        	# Don't try to thumbnail non-image files
        	pass
