"""
=====
Forms
=====

Forms for the MWC Gallery app.
"""
from django import forms
from django.forms.models import modelformset_factory

from mimesis.models import MediaUpload
from mediaman.forms import MetadataForm
from taggit.forms import TagField

from gallery.models import Gallery


class MediaForm(MetadataForm):
    delete = forms.BooleanField(required=False)
       
        
MediaFormSet =  modelformset_factory(
                    MediaUpload,
                    extra=0,
                    form=MediaForm
                )

class GalleryDetailsForm(forms.ModelForm):
    """
    Form for users to provide details for a :class:`gallery.models.Gallery`.  Also provides a :class:`forms.FileField` so that users can upload a zip archive of photos to attach to the gallery.
    
    Updates the labels for the *name*, *description*, and *photos* fields.  The *photos* field also changes based on whether a user is editing or creating a gallery.
    """
    photos = forms.FileField()

    class Meta:
        model = Gallery
        fields = [
                "name",
                "description",
                "tags",
                "sites",
        ]
        
    def __init__(self, *args, **kwargs):
        super(GalleryDetailsForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = "Gallery Name"
        self.fields["description"].label = "Gallery Description"
        if self.instance:
            self.fields["photos"].label = "Add More Photos (zip file)"
        else:
            self.fields["photos"].label = "Photos (zip file)"

class GalleryUpdateForm(forms.Form):
    """
    Simple, one-field form for allowing a user to upload a zip file to be attached to a gallery.
    """
    photos = forms.FileField()

class GalleryDeleteForm(forms.Form):
    """
    Simple form for deleting an existing gallery.
    """
    gallery_id = forms.IntegerField(widget=forms.HiddenInput)
