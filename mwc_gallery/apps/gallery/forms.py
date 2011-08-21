from django import forms
from django.forms.formsets import formset_factory

from mimesis.models import MediaUpload

from gallery.models import Gallery


class PhotoForm(forms.ModelForm):
    
    class Meta:
        model = MediaUpload
        fields = [
                "media",
                "creator",
                "description",
        ]
        widgets = {
            "creator": forms.HiddenInput,
        }
    
    def __init__(self, *args, **kwargs):
        super(PhotoForm,self).__init__(*args, **kwargs)
        self.fields["media"].label = "Picture"
        
PhotoFormSet = formset_factory(PhotoForm, extra=3)

class GalleryDetailsForm(forms.ModelForm):
    class Meta:
        odel = Gallery
