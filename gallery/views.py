"""
=====
Views
=====

Functions listed here are intended to be used as Django views.
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseBadRequest

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from endless_pagination.decorators import page_template

from mimesis.models import MediaUpload

from gallery.forms import MediaFormSet, GalleryDetailsForm, GalleryUpdateForm, GalleryDeleteForm
from gallery.models import Gallery


def gallery_list(request, template="gallery/gallery_list.html"):
    """
    Lists the available galleries.
    
    *Template Name:* gallery/gallery_list.html
    
    **Context Variables**:
    
        * galleries: A QuerySet of :class:`gallery.models.Gallery` instances.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        
    *URL*: <gallery_root>/ 
    """
    
    # @@@ filter them based on public/private?
    galleries = Gallery.objects.all()
    
    ctx = {
        "galleries": galleries,
        "thumbnail_sizes": settings.THUMBNAIL_SIZES,
    }
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request))
        
        
@page_template("gallery/_media_list.html")
def gallery_details(request, gallery_id, template="gallery/gallery_details.html", extra_context=None):
    """
    View a gallery's details.
    
    *Template Name:* gallery/gallery_details.html
    
    **Context Variables**:
    
        * gallery: The :class:`gallery.models.Gallery` that will be displayed
        * media: The :class:`mimesis.models.MediaUpload` objects associated with the gallery.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        
    *URL*: <gallery_root>/<gallery_id>
    """
    
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    
    media = gallery.media.all().order_by("created")
    
    ctx = {
        "gallery": gallery,
        "media": media,
        "thumbnail_sizes": settings.THUMBNAIL_SIZES,
    }
    
    if extra_context:
        ctx.update(extra_context)
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request))
        
        
@login_required
def gallery_create_edit(request, gallery_id=None, template="gallery/gallery_create_edit.html"):
    """
    Create or edit a gallery with a given title, description, and zip file.
    
    This view will take a zip file and create a gallery by expanding it and
    adding the contents as :class:`mimesis.models.MediaUpload` objects, then
    associate those with the new gallery.
    
    Redirects to :func:`gallery_edit_metadata` on creation of a new gallery.
    
    *Template Name*: gallery/gallery_create.html
    
    **Context Variables**:
    
        * gallery_form: A :class:`gallery.forms.GalleryDetailsForm` that allows a user to define the gallery name, a description of the gallery, and attach a zip archive of photos to associate with gallery.
        
    *URL*: <gallery_root>/create -or- <gallery_root>/edit/<gallery_id>/
    """
    if gallery_id:
        gallery = get_object_or_404(Gallery, pk=gallery_id)
    else:
        gallery = None
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
            
            return redirect("gallery_edit_metadata", gallery.pk)
        else:
            messages.error(request, "Could not create new gallery.")
    else:
        if gallery:
            gallery_form = GalleryDetailsForm(instance=gallery)
        else:
            gallery_form = GalleryDetailsForm()
        
    return render_to_response(template, {
        "gallery_form": gallery_form,
    }, context_instance=RequestContext(request))
    
    
@login_required
def gallery_add_media(request, gallery_id, template="gallery/gallery_add_photo.html"):
    """
    Add a media to an existing :class:`gallery.models.Gallery`.
    
    Creates an instance of :class:`gallery.forms.GalleryUpdateForm` to get a user's zip file.
    
    *URL*: <gallery_root>/add_media
    """
    
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    
    if request.method == "POST":
        form = GalleryUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            gallery.from_zip(request.FILES["photos"])
            messages.success(request, "Photos added!")
            return redirect("gallery_edit_metadata", gallery.pk)
    else:
        form = GalleryUpdateForm()
        
    return render_to_response(template, {
        "gallery": gallery,
        "form": form,
    }, context_instance=RequestContext(request))
    
    
@login_required
def gallery_delete(request):
    """
    Delete a gallery and associated media on POST.
    
    *Template Name*: None; redirects back to gallery list.
    
    **Context Variables**:
        
        * None
    
    *URL*: <gallery_root>/delete
    """
    if request.method == "POST":
        form = GalleryDeleteForm(request.POST)
        if form.is_valid():
            gallery = Gallery.objects.get(id=form.cleaned_data["gallery_id"])
            
            gallery_name = gallery.name
            
            gallery.delete()
            
            messages.success(request, "Gallery '%s' was deleted." % gallery_name)
            return redirect("gallery_list")
    return HttpResponseBadRequest("Not a POST request or bad POST data.")
            
            
@login_required
@page_template("gallery/_edit_media_details.html")
def gallery_edit_metadata(request, gallery_id, template="gallery/gallery_edit_metadata.html", extra_context=None):
    """
    Allows a user to edit details and media tied to an existing gallery.
    
    This view will return a :class:`gallery.forms.MediaFormSet` that allows users to view the uploaded media, as well as change it's caption and tags.
    
    Additionally, the user can use this form to delete an image or set it as the gallery's primary image.  This means it will display as the gallery's thumbnail.
    
    *Template Name*: gallery/gallery_edit_metadata.html (gallery/_media_form.html as a subtemplate, gallery/_edit_media_details.html for AJAX list loading.)
    
    **Context Variables**:
    
        * gallery: A :class:`gallery.models.Gallery` instance that references the photos the user will edit.
        * media_formset: A :class:`gallery.forms.MediaFormSet` that uses all the media attached to the `gallery` variable as it's QuerySet data.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        * paginate_count: Number of items to be displayed per page. (interface to settings.PAGINATE_COUNT)
        
    *URL*: <gallery_root>/edit_metadata
    """
    
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
                    # Work around a bug where the form's instance is a MediaUpload object
                    # with the correct id, but is missing the media property.
                    # This allows editing multiple images with endless-pagination to work.
                    m = MediaUpload.objects.get(id=form.cleaned_data['id'].id)
                    form.instance = m
                    form.save()
            messages.success(request, "Gallery updated.")
            return redirect(reverse("gallery_details", args=(gallery.id,)))

        else:
            # NOTE: Here we don't "rewind" the pagination; if there's an error, the user has to start at the top,
            # losing their place.
            messages.error(request, "Could not update gallery.")
    else:
        update_formset = True
        
    if update_formset:
        media_formset = MediaFormSet(queryset=gallery.media.all().order_by("created"))
        
    delete_form = GalleryDeleteForm({"gallery_id": gallery.id})
    
    ctx = {
        "gallery": gallery,
        "media_formset": media_formset,
        "delete_form": delete_form,
        "thumbnail_sizes": settings.THUMBNAIL_SIZES,
        "paginate_count": settings.PAGINATE_COUNT,
    }
    
    if extra_context is not None:
        ctx.update(extra_context)
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request)
    )
    
    
@login_required
def gallery_image_details(request, gallery_id, media_id, template="gallery/gallery_image_details.html"):
    """
    Returns full details of an image, and the full image for individual viewing.
    
    *Template Name*: gallery/gallery_image_details.html
    
    **Context Variables**:
    
        * media: A :class:`mimesis.models.MediaUpload` object that is associated with the requested :class:`gallery.models.Gallery`
        
    *URL*: <gallery_root>/<gallery_id>/image_details/<image_id>
    """
    
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    media = get_object_or_404(gallery.media, pk=media_id)
    
    ctx = {
        "media": media,
    }
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request)
    )
    
