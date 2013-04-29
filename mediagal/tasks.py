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

@task
def update_gallery_captions(gallery_id, request_post):
    from mediagal.models import Gallery
    from mediagal.forms import MediaFormSet

    media_formset = MediaFormSet(request_post)
    gallery = Gallery.objects.get(pk=gallery_id)
    if media_formset.is_valid():
        for form in media_formset.forms:
            if form.cleaned_data["delete"]:
                deleted = gallery.remove_media(form.cleaned_data["id"])
            else:
                if "cover_image" in request_post:
                    if form.cleaned_data["id"].id == int(request_post["cover_image"]):
                        # set the gallery's cover image to the media object
                        gallery.cover = form.instance
                        gallery.save()
                form.save()

    print "updated gallery."