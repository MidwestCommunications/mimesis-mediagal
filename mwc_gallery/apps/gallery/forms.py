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
        ]
        widgets = {
            "creator": forms.HiddenInput,
        }

PhotoFormSet = formset_factory(PhotoForm, extra=3)

class GalleryDetailsForm(forms.ModelForm):
    class Meta:
        model = Gallery
