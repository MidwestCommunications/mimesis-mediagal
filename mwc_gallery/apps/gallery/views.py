from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from mimesis.models import MediaUpload
from uploadify.views import upload_received

from gallery.forms import MediaFormSet, GalleryDetailsForm
from gallery.models import Gallery, GalleryMedia


def upload_received_handler(sender, data, user, **kwargs):
    mu = MediaUpload.objects.create(
            media=data,
            creator=user
        )
    # @@@ Need some way of indicating that these files need to be associated with a gallery.
    # Possibly by changing the GalleryMedia to have a nullable gallery attribute, creating them here,
    # then populating the Gallery attribute when the gallery is fully created?
    
upload_received.connect(upload_received_handler, dispatch_uid="gallery.upload_received")


def gallery_list(request):
    """
    Lists the available galleries.
    """

    template_name = "gallery/gallery_list.html"

    # @@@ filter them based on public/private?
    galleries = Gallery.objects.all()

    return render_to_response(template_name, {
        "galleries": galleries,
    }, context_instance=RequestContext(request))


def gallery_details(request, gallery_id):
    """
    View a gallery.
    """

    template_name = "gallery/gallery_details.html"

    gallery = get_object_or_404(Gallery, pk=gallery_id)

    media = gallery.media.all()

    return render_to_response(template_name, {
        "gallery": gallery,
        "media": media,
    }, context_instance=RequestContext(request))


@login_required
def gallery_create(request):
    """
    Create a gallery.
    """

    template_name = "gallery/gallery_create.html"
    if request.method == "POST":
        media_formset = MediaFormSet(request.POST, request.FILES)
        gallery_form = GalleryDetailsForm(request.POST)

        if media_formset.is_valid() and gallery_form.is_valid():
            items = []
            for form in media_formset.forms:
                media_item = form.save()
                if media_item.media_type == "image":
                    media_item.save()
                    items += [media_item]
            if items:
                g_name = gallery_form.cleaned_data["name"]
                g_desc = gallery_form.cleaned_data["description"]
                gallery = Gallery(
                        name=g_name,
                        description=g_desc,
                        owner=request.user,
                )
                gallery.save()

                for media in items:
                    GalleryMedia.objects.create(media=media, gallery=gallery)

                print "Gallery created."
                return redirect("gallery_list")
            else:
                print "No items!"
        else:
            pass
    else:
        initial_media_data = [{"creator": request.user.pk}]

        media_formset = MediaFormSet(initial=initial_media_data)

        gallery_form = GalleryDetailsForm()

    return render_to_response(template_name, {
        "gallery_form": gallery_form,
        "media_formset": media_formset
    }, context_instance=RequestContext(request))


def gallery_add_media(request):
    """
    Add a media to the gallery.
    """

    pass


def gallery_remove_media(request):
    """
    Remove a media from a gallery.
    """

    pass


def gallery_delete(request):
    """
    Delete a gallery.
    """

    pass
    
    
@login_required
def gallery_bulk_create(request):
    template_name = "gallery/gallery_bulk_create.html"
    ctx = {}
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
    

@login_required
def gallery_images_uploaded(request):
    
    template_name = "gallery/gallery_images_uploaded.html"
    if request.POST:
        print request.POST
        # Get ids for all of this user's uploads that are not associated with a gallery.
        uploads = MediaUpload.objects.filter(creator=request.user.pk, gallerymedia__isnull=True).values_list("pk", flat=True)
        ctx = {"uploads": uploads}
    else:
        ctx = {"invalid_request": True}
        
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
    
    
@login_required
def gallery_edit_details(request):
    
    template_name = "gallery/gallery_edit_details.html"
    
    import pdb; pdb.set_trace()
    if request.POST:
        if "media" in request.POST:
            media_pks = request.POST.getlist("media")
            media_list = MediaUpload.objects.filter(pk__in=media_pks)
            # @@ create a formset that will include image thumbnails, so the user knows what they're editing.
            # For now, we'll just send the media list on to the template
            ctx = {"media": media_list}
        else:
            ctx = {"media": None}
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
    
    
@login_required
def gallery_resource_upload(request):

    if request.method == "POST":
        for key in request.FILES:
            MediaUpload.objects.create(
                media=request.FILES[key],
                creator_id=request.user.pk
            )
    return HttpResponse("ok", mimetype="text/plain")
