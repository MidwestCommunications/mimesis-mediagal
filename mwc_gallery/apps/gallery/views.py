"""
=====
Views
=====

Functions listed here are intended to be used as Django views.
"""

from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from mimesis.models import MediaUpload
from uploadify.views import upload_received

from apps.gallery.forms import MediaFormSet, GalleryDetailsForm
from apps.gallery.models import Gallery, GalleryMedia


def upload_received_handler(sender, data, user, **kwargs):
    """
    .. admonition:: Relocate
    
        Since this is a signal handler, not a view function, this should probably be moved somewhere else.
        
    Handler for the django-uploadify upload_received signal. It creates a :class:`mimesis.models.MediaUpload`,
    which in turn creates the actual file and associates it with a user.
    
    Some future work might be to flag the object as being not associated with a gallery.
    
    """
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
    
    *Template Name:* gallery/gallery_list.html
    
    **Context Variables**:
    
        * galleries: A QuerySet of :class:`apps.gallery.models.Gallery` instances.
        
    *URL*: <gallery_root>/ 
    """

    template_name = "gallery/gallery_list.html"

    # @@@ filter them based on public/private?
    galleries = Gallery.objects.all()

    return render_to_response(template_name, {
        "galleries": galleries,
    }, context_instance=RequestContext(request))


def gallery_details(request, gallery_id):
    """
    View a gallery's details.
    
    *Template Name:* gallery/gallery_details.html
    
    **Context Variables**:

        * gallery: The :class:`apps.gallery.models.Gallery` that will be displayed
        * media: The :class:`mimesis.models.MediaUpload` objects associated with the gallery.
        
    *URL*: <gallery_root>/<gallery_id>
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
    Create a gallery using standard HTML forms.
    
    *Template Name*: gallery/gallery_create.html
    
    **Context Variables**:
    
        * gallery_form: A :class:`apps.gallery.forms.GalleryDetailsForm` that allows a user to define the gallery name and a description of the gallery.
        * media_formset: A :class:`apps.gallery.forms.MediaForm` formset that allows a user to attach a file and a description of said file. Initial data for this formset includes the creating user's PK.
        
    *URL*: <gallery_root>/create
    """

    template_name = "gallery/gallery_create.html"
    if request.method == "POST":
        # @@@ Attempt to make this view viable for both the 'bulk uploader' and normal forms;
        # it doesn't work.
        if request.FILES:
            media_formset = MediaFormSet(request.POST, request.FILES)
        else:
            media_formset = MediaFormSet(request.POST)
            
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
    Add a media to an existing :class:`apps.gallery.models.Gallery`.
    
    *URL*: <gallery_root>/add_media
    """

    pass


def gallery_remove_media(request):
    """
    Remove a media item from a gallery.
    
    *URL*: <gallery_root>/remove_media
    """

    pass


def gallery_delete(request):
    """
    Delete a gallery and associated media.
    
    *URL*: <gallery_root>/delete
    """

    pass
    
    
@login_required
def gallery_bulk_create(request):
    """
    Starting point for using a Flash bulk uploader to create a new gallery.
    
    *Template Name*: gallery/gallery_bulk_create.html
    
    **Context Variables**:
    
        * None
    
    *URL*: <gallery_root>/bulk_create
    """

    template_name = "gallery/gallery_bulk_create.html"
    ctx = {}
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
    

@login_required
def gallery_images_uploaded(request):
    """
    Returns a form with the PKs of MediaUpload objects created by the django-uploadify uploaded signal.
    
    This should only be through POST requests right now, since django-uploadify has this URL as it's "upload-finished" URL.
    
    *Template Name:* gallery/gallery_images_uploaded.html
    
    **Context Variables**:
    
        * uploads: List of primary keys for :class:`mimesis.models.MediaUpload` objects that belong to the requesting user and aren't in a gallery yet.
        * invalid_request: Flag that indicates if the view was accessed with a GET.

    *URL*: <gallery_root>/images_uploaded
    """
    
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
    """
    Allows a user to edit details and media tied to an existing gallery.
    
    This is the 'final' endpoint in chain of bulk-upload URLs, but probably should be used independently.
    
    *Template Name*: gallery/gallery_edit_details.html
    
    **Context Variables**:
    
        * media: QuerySet of :class:`mimesis.models.MediaUpload` objects that were requested from a POST, or empty when none are POSTed
        * gallery_form: Instance of :class:`apps.gallery.forms.GalleryDetailsForm` for inputting gallery name and description.
        * media_formset: Set of :class:`apps.gallery.forms.MediaForm` of the media associated with the gallery. Initial data includes the creators, primary key, and the media itself.
        
    *URL*: <gallery_root>/edit_details
    """
    
    template_name = "gallery/gallery_edit_details.html"
    
    import pdb; pdb.set_trace()
    if request.POST:
        if "media" in request.POST:
            media_pks = request.POST.getlist("media")
            media_list = MediaUpload.objects.filter(pk__in=media_pks)
            initial_media_data = [
                    {"creator": media.creator,
                    "pk": media.pk,
                    "media": media.media}
                    for media in media_list
            ]

            media_formset = MediaFormSet(initial=initial_media_data)
        else:
            media_list = None
            media_formset = None
        
        ctx = {
            "media": media_list,
            "gallery_form": GalleryDetailsForm(),
            "media_formset": media_formset,
        }
    return render_to_response(template_name, ctx,
        context_instance=RequestContext(request)
    )
    
    
@login_required
def gallery_resource_upload(request):
    """
    .. admonition:: Deprecated
    
        This function was used in an earlier attempt to integrate SWFUpload.
    
    Endpoint for SWFUpload to upload a file to.

    """

    if request.method == "POST":
        for key in request.FILES:
            MediaUpload.objects.create(
                media=request.FILES[key],
                creator_id=request.user.pk
            )
    return HttpResponse("ok", mimetype="text/plain")
