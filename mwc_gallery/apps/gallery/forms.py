from django import forms
from django.forms.formsets import formset_factory

from mimesis.models import MediaUpload
from mediaman.forms import MediaModelForm

from apps.gallery.models import Gallery


class MediaForm(MediaModelForm):
    
    class Meta:
        model = MediaUpload
        fields = [
                "creator",
                "media",
                "caption",
        ]
        widgets = {
            "creator": forms.HiddenInput,
        }
    
    def __init__(self, *args, **kwargs):
        super(MediaForm,self).__init__(*args, **kwargs)
        self.fields["caption"].label = "Media Description"
        
MediaFormSet = formset_factory(MediaForm, extra=0)

class GalleryDetailsForm(forms.ModelForm):
    
    class Meta:
        model = Gallery
        fields = [
                "name",
                "description",
        ]
        
    def __init__(self, *args, **kwargs):
        super(GalleryDetailsForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = "Gallery Name"
        self.fields["description"].label = "Gallery Description"
