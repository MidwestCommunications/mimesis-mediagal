
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from gallery.forms import PhotoFormSet, GalleryDetailsForm
from gallery.models import Gallery, GalleryPhotos

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
    
    photos = gallery.photos.all()
    
    return render_to_response(template_name, {
        "gallery": gallery,
        "photos": photos,
    }, context_instance=RequestContext(request))
    
@login_required
def gallery_create(request):
    """
    Create a gallery.
    """
    
    template_name = "gallery/gallery_create.html"
    if request.method == "POST":
        photo_formset = PhotoFormSet(request.POST, request.FILES)
        gallery_form = GalleryDetailsForm(request.POST)

        if photo_formset.is_valid() and gallery_form.is_valid():
            photos = []
            for form in photo_formset.forms:
                media_item = form.save()
                if media_item.media_type == "image":
                    media_item.save()
                    photos += [media_item]
            if photos:
                g_name = gallery_form.cleaned_data["name"]
                g_desc = gallery_form.cleaned_data["description"]
                gallery = Gallery(
                        name=g_name,
                        description=g_desc,
                        owner=request.user,
                )
                gallery.save()

                for photo in photos:
                    GalleryPhotos.objects.create(photo=photo, gallery=gallery)

                print "Gallery created."
                return redirect("gallery_list")
            else:
                print "No photos!"
                #import pdb; pdb.set_trace()
        else:
            #import pdb; pdb.set_trace()
            pass
    else:
        initial_photo_data = [{"creator": request.user.pk}] * 3
        
        photo_formset = PhotoFormSet(initial=initial_photo_data)

        gallery_form = GalleryDetailsForm()
        
    
    return render_to_response(template_name, {
        "gallery_form": gallery_form,
        "photo_formset": photo_formset
    }, context_instance=RequestContext(request))
    
def gallery_add_photo(request):
    """
    Add a photo to the gallery.
    """
    
    pass
    
    
def gallery_remove_photo(request):
    """
    Remove a photo from a gallery.
    """
    
    pass
    
    
def gallery_delete(request):
    """
    Delete a gallery.
    """
    
    pass
    
    
