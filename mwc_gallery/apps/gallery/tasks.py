"""
====
Tasks
====

Tasks are provided for the Celery job management library that generate thumbnails for uploaded images in the background.
"""

from celery.task import task

from easy_thumbnails.files import get_thumbnailer, ThumbnailFile

def square_thumbnail(source, size):
    """
    Generates a square thumbnail from a source image, saving the thumbnail to the specified out_path.
    """
    thumbnail_options = {"size": size, "crop": True}

    thumbnailer = get_thumbnailer(source)
    
    return thumbnailer.get_thumbnail(thumbnail_options)


@task
def generate_thumbnail(image, ratio, *args, **kwargs):
    """
    Creates a new image of the given ratio, saving it to the provided output path.
    """
    
    thumbnail = square_thumbnail(image, ratio)
    
