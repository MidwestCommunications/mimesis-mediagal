"""
=====
Views
=====

Functions listed here are intended to be used as Django views.
"""

from django.conf import settings
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from gallery.forms import MediaFormSet, GalleryDetailsForm, GalleryUpdateForm
from gallery.models import Gallery


def gallery_list(request):
    """
    Lists the available galleries.
    
    *Template Name:* gallery/gallery_list.html
    
    **Context Variables**:
    
        * galleries: A QuerySet of :class:`gallery.models.Gallery` instances.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        
    *URL*: <gallery_root>/ 
    """

    template_name = "gallery/gallery_list.html"

    # @@@ filter them based on public/private?
    galleries = Gallery.objects.all()
    
    ctx = {
        "galleries": galleries,
        "thumbnail_sizes": settings.THUMBNAIL_SIZES,
    }

    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request))


def gallery_details(request, gallery_id):
    """
    View a gallery's details.
    
    *Template Name:* gallery/gallery_details.html
    
    **Context Variables**:

        * gallery: The :class:`gallery.models.Gallery` that will be displayed
        * media: The :class:`mimesis.models.MediaUpload` objects associated with the gallery.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        
    *URL*: <gallery_root>/<gallery_id>
    """

    template_name = "gallery/gallery_details.html"

    gallery = get_object_or_404(Gallery, pk=gallery_id)

    media = gallery.media.all().order_by("created")
    
    ctx = {
        "gallery": gallery,
        "media": media,
        "thumbnail_sizes": settings.THUMBNAIL_SIZES,
    }

    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request))


@login_required
def gallery_create(request):
    """
    Create a gallery using standard HTML forms.
    
    Redirects to :func:`gallery_edit_details` on creation of a new gallery.
    
    *Template Name*: gallery/gallery_create.html
    
    **Context Variables**:
    
        * gallery_form: A :class:`gallery.forms.GalleryDetailsForm` that allows a user to define the gallery name, a description of the gallery, and attach a zip archive of photos to associate with gallery.
        
    *URL*: <gallery_root>/create
    """

    template_name = "gallery/gallery_create.html"
    if request.method == "POST":
        gallery_form = GalleryDetailsForm(request.POST, request.FILES)

        if gallery_form.is_valid():
            # @@@ check for duplicated gallery names?
            g_name = gallery_form.cleaned_data["name"]
            g_desc = gallery_form.cleaned_data["description"]
            gallery = Gallery(
                    name=g_name,
                    description=g_desc,
                    owner=request.user,
            )
            gallery.save()
            for site in gallery_form.cleaned_data["sites"]:
                gallery.add_site(site)
            gallery.from_zip(request.FILES["photos"], initial=True)
            
            messages.success(request, "Created gallery '%s'" % gallery.name)

            return redirect("gallery_edit_details", gallery.pk)
        else:
            messages.error(request, "Could not create new gallery.")
    else:
        gallery_form = GalleryDetailsForm()

    return render_to_response(template_name, {
        "gallery_form": gallery_form,
    }, context_instance=RequestContext(request))

@login_required
def gallery_add_media(request, gallery_id):
    """
    Add a media to an existing :class:`gallery.models.Gallery`.
    
    Creates an instance of :class:`gallery.forms.GalleryUpdateForm` to get a user's zip file.
    
    *URL*: <gallery_root>/add_media
    """

    template_name = "gallery/gallery_add_photo.html"
    
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    
    if request.method == "POST":
        form = GalleryUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            gallery.from_zip(request.FILES["photos"])
            messages.success(request, "Photos added!")
            return redirect("gallery_edit_details", gallery.pk)
    else:
        form = GalleryUpdateForm()
    
    return render_to_response(template_name, {
        "gallery": gallery,
        "form": form,
    }, context_instance=RequestContext(request))


def gallery_delete(request):
    """
    Delete a gallery and associated media.
    
    *URL*: <gallery_root>/delete
    """

    pass
    
    
    
@login_required
def gallery_edit_details(request, gallery_id):
    """
    Allows a user to edit details and media tied to an existing gallery.
    
    This view will return a :class:`gallery.forms.MediaFormSet` that allows users to view the uploaded media, as well as change it's caption and tags.
    
    Additionally, the user can use this form to delete an image or set it as the gallery's primary image.  This means it will display as the gallery's thumbnail.
    
    *Template Name*: gallery/gallery_edit_details.html (gallery/_media_form.html as a subtemplate)
    
    **Context Variables**:
        
        * gallery: A :class:`gallery.models.Gallery` instance that references the photos the user will edit.
        * media_formset: A :class:`gallery.forms.MediaFormSet` that uses all the media attached to the `gallery` variable as it's QuerySet data.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)

    *URL*: <gallery_root>/edit_details
    """
    
    template_name = "gallery/gallery_edit_details.html"
    
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    
    if request.method == "POST":
        update_formset = False

        media_formset = MediaFormSet(request.POST)
        if media_formset.is_valid():
            for form in media_formset.forms:
                if form.cleaned_data["delete"]:
                    deleted = gallery.remove_media(form.cleaned_data["id"])
                    if not deleted:
                        messages.error(request, "Could not delete image")
                    else:
                        # If media was deleted, we need to refresh the formset from the database,
                        # since otherwise the formset would still contain items from the POST that
                        # requested deletion.
                        update_formset = True
                else:
                    if "cover_image" in request.POST:
                        if form.cleaned_data["id"].id == int(request.POST["cover_image"]):
                            # set the gallery's cover image to the media object
                            gallery.cover = form.instance
                            gallery.save()
                    form.save()

            messages.success(request, "Gallery updated.")
        else:
            messages.error(request, "Could not update gallery.")
    else:
        update_formset = True
    
    if update_formset:
        media_formset = MediaFormSet(queryset=gallery.media.all().order_by("created"))

    ctx = {
        "gallery": gallery,
        "media_formset": media_formset,
        "thumbnail_sizes": settings.THUMBNAIL_SIZES,
    }
    
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
    
@login_required
def gallery_image_details(request, gallery_id, media_id):
    """
    Returns full details of an image, and the full image for individual viewing.
    
    *Template Name*: gallery/gallery_image_details.html
    
    **Context Variables**:
    
        * media: A :class:`mimesis.models.MediaUpload` object that is associated with the requested :class:`gallery.models.Gallery`
        
    *URL*: <gallery_root>/<gallery_id>/image_details/<image_id>
    """
    
    template_name = "gallery/gallery_image_details.html"
    
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    media = get_object_or_404(gallery.media, pk=media_id)
    
    ctx = {
        "media": media,
    }
    
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
