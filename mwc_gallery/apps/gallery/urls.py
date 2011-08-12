from django.conf.urls.defaults import *

urlpatterns = patterns("galleries.views",
    url(r"^$", "gallery_list", name="gallery_list"),
    url(r"create$", "gallery_create", name="gallery_create"),
    url(r"add_photo$", "gallery_add_photo", name="gallery_add_photo"),
    url(r"remove_photo$", "gallery_remove_phot", name="gallery_remove_photo"),
    url(r"delete$", "gallery_delete", name="gallery_delete"),
)
