from django.conf.urls.defaults import *

urlpatterns = patterns("mediagal.views",
    url(r"^$", "gallery_list", name="mediagal_gallery_list"),
    url(r"^(\d+)/$", "gallery_details", name="mediagal_gallery_details"),
    url(r"^create/$", "gallery_create_edit", name="mediagal_gallery_create"),
    url(r"^edit/(\d+)/$", "gallery_create_edit", name="mediagal_gallery_edit"),
    url(r"^delete/$", "gallery_delete", name="mediagal_gallery_delete"),
    url(r"edit_images/(\d+)/$", "edit_gallery_images", name="mediagal_edit_gallery_images"),
    url(r"^(\d+)/image/(\d+)/$", "image_details", name="mediagal_image_details"),
)
