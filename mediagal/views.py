"""
=====
Views
=====

Functions listed here are intended to be used as Django views.
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import redirect, render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, Http404

from django.contrib import messages
from django.contrib.sites.models import Site, get_current_site
from django.contrib.auth.decorators import login_required

from mimesis.models import MediaUpload
from mediaman.forms import MetadataForm

from mediagal.forms import MediaFormSet, GalleryDetailsForm, GalleryDeleteForm, MediaDeleteForm
from mediagal.models import Gallery, GalleryMedia
from mediagal.tasks import update_gallery_captions


def _check_attached(media_upload, exclude_gallery=None):
    if media_upload.gallerymedia_set.exclude(gallery=exclude_gallery).exists():
        return True
    if media_upload.mediaassociation_set.exists():
        return True
    return False


def gallery_list(request, template="mediagal/gallery_list.html"):
    """
    Lists the available galleries.
    
    *Template Name:* mediagal/gallery_list.html
    
    **Context Variables**:
    
        * galleries: A QuerySet of :class:`gallery.models.Gallery` instances.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        
    *URL*: <gallery_root>/ 
    """
    
    current_site = get_current_site(request)
    
    galleries = Gallery.objects.filter(sites=current_site).annotate(media_count=Count("media")).select_related('cover')
    
    ctx = {
        "galleries": galleries,
    }
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request))
        
        
def gallery_details(request, gallery_id, template="mediagal/gallery_details.html", extra_context=None):
    """
    View a gallery's details.
    
    *Template Name:* mediagal/gallery_details.html
    
    **Context Variables**:
    
        * gallery: The :class:`gallery.models.Gallery` that will be displayed
        * media: The :class:`mimesis.models.MediaUpload` objects associated with the gallery.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        
    *URL*: <gallery_root>/<gallery_id>
    """
    
    site = get_current_site(request)
    gallery = get_object_or_404(Gallery, pk=gallery_id, sites=site)
    
    media = gallery.media.all().order_by("-created")
    delete_form = GalleryDeleteForm({"gallery_id": gallery.id})
    
    ctx = {
        "gallery": gallery,
        "media": media,
        "delete_form": delete_form,
    }
    
    if extra_context:
        ctx.update(extra_context)
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request))
        
        
@login_required
def gallery_create_edit(request, gallery_id=None, template="mediagal/gallery_create_edit.html"):
    """
    Create or edit a gallery with a given title, description, and zip file.
    
    This view will take a zip file and create a gallery by expanding it and
    adding the contents as :class:`mimesis.models.MediaUpload` objects, then
    associate those with the new gallery.
    
    Redirects to :func:`gallery_edit_metadata` on creation of a new gallery.
    
    *Template Name*: mediagal/gallery_create.html
    
    **Context Variables**:
    
        * gallery_form: A :class:`gallery.forms.GalleryDetailsForm` that allows a user to define the gallery name, a description of the gallery, and attach a zip archive of photos to associate with gallery.
        
    *URL*: <gallery_root>/create -or- <gallery_root>/edit/<gallery_id>/
    """
    if gallery_id:
        gallery = get_object_or_404(Gallery, pk=gallery_id)
        action = "Edit"
    else:
        gallery = None
        action = "Create"
        
    if request.method == "POST":
        gallery_form = GalleryDetailsForm(request.POST, request.FILES, instance=gallery)
        
        if gallery_form.is_valid():
            # @@@ check for duplicated gallery names?
            g_name = gallery_form.cleaned_data["name"]
            g_desc = gallery_form.cleaned_data["description"]
            g_tags = gallery_form.cleaned_data["tags"]
            
            if gallery:
                gallery.name = g_name
                gallery.description = g_desc
                initial = False
            else:
                gallery = gallery_form.save(commit=False)
                gallery.owner = request.user
                initial = True

            gallery.save()
            
            gallery.tags.set(*g_tags)
            
            for site in gallery_form.cleaned_data["sites"]:
                gallery.add_site(site)
            
            if gallery_form.cleaned_data["photos"]:
                gallery.from_zip(gallery_form.cleaned_data["photos"], initial=initial)
            
            messages.success(request, "%sed gallery '%s'" % (action, gallery.name))
            
            return redirect("mediagal_edit_gallery_images", gallery.pk)
        else:
            messages.error(request, "Could not %s gallery" % action.lower())
    else:
        if gallery:
            gallery_form = GalleryDetailsForm(instance=gallery)
        else:
            gallery_form = GalleryDetailsForm()
        
    return render(request, template, {
        "gallery_form": gallery_form,
        "action": action,
    })


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
            return redirect("mediagal_gallery_list")
    return HttpResponseBadRequest("Not a POST request or bad POST data.")
            
            
@login_required
def edit_gallery_images(request, gallery_id, template="mediagal/edit_gallery_images.html", extra_context=None):
    """
    Allows a user to edit details and media tied to an existing gallery.
    
    This view will return a :class:`gallery.forms.MediaFormSet` that allows users to view the uploaded media, as well as change it's caption and tags.
    
    Additionally, the user can use this form to delete an image or set it as the gallery's primary image.  This means it will display as the gallery's thumbnail.
    
    *Template Name*: mediagal/gallery_edit_metadata.html (mediagal/_media_form.html as a subtemplate, mediagal/_edit_media_details.html for AJAX list loading.)
    
    **Context Variables**:
    
        * gallery: A :class:`gallery.models.Gallery` instance that references the photos the user will edit.
        * media_formset: A :class:`gallery.forms.MediaFormSet` that uses all the media attached to the `gallery` variable as it's QuerySet data.
        * thumbnail_sizes: Dictionary of thumbnail sizes (interface to settings.THUMBNAIL_SIZES)
        * paginate_count: Number of items to be displayed per page. (interface to settings.PAGINATE_COUNT)
        
    *URL*: <gallery_root>/edit_metadata
    """
    
    site = get_current_site(request)
    gallery = get_object_or_404(Gallery, pk=gallery_id, sites=site)
    
    if request.method == "POST":
        
        #media_formset = MediaFormSet(request.POST)
        

        update_gallery_captions.delay(gallery.pk, request.POST)
        messages.success(request, "Gallery updated.")
        return redirect(reverse("mediagal_gallery_details", args=(gallery.id,)))

        #else:
        # NOTE: Here we don't "rewind" the pagination; if there's an error, the user has to start at the top,
        # losing their place.
        #messages.error(request, "Could not update gallery.")
        
    media_formset = MediaFormSet(queryset=gallery.media.all().order_by("-created"))
        
    ctx = {
        "gallery": gallery,
        "media_formset": media_formset,
        "paginate_count": settings.PAGINATE_COUNT,
    }
    
    if extra_context is not None:
        ctx.update(extra_context)
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request)
    )
    
    
def image_details(request, gallery_id, media_id, template="mediagal/image_details.html"):
    """
    Returns full details of an image, and the full image for individual viewing.
    
    *Template Name*: mediagal/gallery_image_details.html
    
    **Context Variables**:
    
        * gallery: A :class:`gallery.models.Gallery` instance that is the parent container of the requested :class:`mimesis.models.MediaUpload`
        * media: A :class:`mimesis.models.MediaUpload` object that is associated with the requested :class:`gallery.models.Gallery`
        
    *URL*: <gallery_root>/<gallery_id>/image_details/<image_id>
    """
    
    site = get_current_site(request)
    gallery = get_object_or_404(Gallery, pk=gallery_id, sites=site)
    media = get_object_or_404(gallery.media, pk=media_id)

    try:
        next_media = media.get_next_by_created(galleries=gallery)
    except MediaUpload.DoesNotExist:
        next_media = MediaUpload.objects.filter(galleries=gallery).order_by('created')[0]
    try:
        prev_media = media.get_previous_by_created(galleries=gallery)
    except MediaUpload.DoesNotExist:
        prev_media = MediaUpload.objects.filter(galleries=gallery).order_by('-created')[0]

    ctx = {
        "gallery": gallery,
        "media": media,
        "attached": _check_attached(media, gallery),
        "next": next_media,
        "prev": prev_media,
    }
    
    return render_to_response(template, ctx,
        context_instance=RequestContext(request)
    )


@login_required
def ajax_metadata_edit(request, gallery_id, media_id):
    if not request.user.is_staff:
        raise Http404
    
    site = get_current_site(request)
    gallery = get_object_or_404(Gallery, pk=gallery_id, sites=site)
    media = get_object_or_404(MediaUpload, pk=media_id)
    attached = _check_attached(media, gallery)

    if request.method == 'POST':
        if attached:
            return HttpResponse(
                'Media is already attached elsewhere and cannot be edited.',
                status_code=409,
                content_type='text/plain'
            )
        edit_form = MetadataForm(request.POST, instance=media)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponse('SUCCESS')
    else:
        edit_form = MetadataForm(instance=media)

    post_url = reverse('mediagal_ajax_metadata_edit', args=[gallery_id, media_id])
    return render(request, 'mediagal/ajax_metadata_edit.html',
        {'form': edit_form, 'post_url': post_url})


@login_required
def ajax_media_delete(request, gallery_id):
    if not request.user.is_staff:
        raise Http404
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    form = MediaDeleteForm(request.POST)
    if form.is_valid():
        rel = GalleryMedia.objects.filter(
            gallery__id=gallery_id,
            media__id=form.cleaned_data['media_id']
        )
        if rel:
            rel.delete()
            return HttpResponse('SUCCESS')
    return HttpResponseBadRequest()
