from django.conf.urls.defaults import *

urlpatterns = patterns("gallery.views",
    url(r"^$", "gallery_list", name="gallery_list"),
    url(r"^(\d+)$", "gallery_details", name="gallery_details"),
    url(r"^create$", "gallery_create", name="gallery_create"),
    url(r"^add_media/(\d+)$", "gallery_add_media", name="gallery_add_media"),
    url(r"^remove_media$", "gallery_remove_media", name="gallery_remove_media"),
    url(r"^delete$", "gallery_delete", name="gallery_delete"),
    url(r"edit_details/(\d+)$", "gallery_edit_details", name="gallery_edit_details"),
)
