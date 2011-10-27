from django.contrib import admin

from apps.gallery.models import Gallery, GalleryMedia, GallerySites

admin.site.register(Gallery)
admin.site.register(GalleryMedia)
admin.site.register(GallerySites)
