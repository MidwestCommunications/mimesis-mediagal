
from django.shortcuts import redirect, render_to_response 
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from gallery.forms import PhotoFormSet, GalleryDetailsForm
from gallery.models import Gallery

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
    
    
def gallery_view(request):
    """
    View a gallery.
    """
    
    pass
    
@login_required
def gallery_create(request):
    """
    Create a gallery.
    """
    
    template_name = "gallery/gallery_create.html"
    if request.method == "POST":
        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix="photos")
        gallery_form = GalleryDetailsForm(request.POST, prefix="gallery")

        if photo_formset.is_valid() and gallery_form.is_valid():
            import pdb; pdb.set_trace()
            photos = []
            # @@@ Need another form to give gallery it's name.
            for form in photo_formset.forms():
                media_item = form.save(commit=False)
                if media_item.media_type == "image":
                    photos += [media_item]
            if photos:
                gallery = Gallery(photos=photos)
                gallery.save()

            redirect("gallery_list")
        else:
            import pdb; pdb.set_trace()
    else:
        initial_photo_data = [{"creator": request.user.pk}] * 3
        
        photo_formset = PhotoFormSet(initial=initial_photo_data, prefix="photos")

        gallery_form = GalleryDetailsForm(prefix="gallery")
        
    
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
    
    
