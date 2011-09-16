
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from gallery.forms import MediaFormSet, GalleryDetailsForm
from gallery.models import Gallery, GalleryMedia

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
        initial_media_data = [{"creator": request.user.pk}] * 3
        
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
    
    
