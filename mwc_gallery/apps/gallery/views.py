
from django.shortcuts import render_to_response
from django.template import RequestContext

from gallery.forms import PhotoForm
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
    
    
def gallery_create(request):
    """
    Create a gallery.
    """
    
    template_name = "gallery/gallery_create.html"
    
    form = PhotoForm(initial={"creator": request.user})
    
    return render_to_response(template_name, {
        "form": form
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
    
    
