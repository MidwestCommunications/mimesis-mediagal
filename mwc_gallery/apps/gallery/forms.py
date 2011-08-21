from django import forms
from django.forms.formsets import formset_factory

from mimesis.models import MediaUpload

from gallery.models import Gallery


class PhotoForm(forms.ModelForm):
    
    media = forms.FileField(
            widget=forms.FileInput(
                attrs={"accept": "image/gif, image/jpeg, image/png"}
            )
    )
    class Meta:
        model = MediaUpload
        fields = [
                "creator",
                "description",
        ]
        widgets = {
            "creator": forms.HiddenInput,
        }
    
    def __init__(self, *args, **kwargs):
        super(PhotoForm,self).__init__(*args, **kwargs)
        self.fields["media"].label = "Picture"
        
PhotoFormSet = formset_factory(PhotoForm, extra=0)

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
