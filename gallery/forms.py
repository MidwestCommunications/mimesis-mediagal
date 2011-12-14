"""
=====
Forms
=====

Forms for the MWC Gallery app.
"""
from django import forms
from django.forms.models import modelformset_factory

from mimesis.models import MediaUpload
from mediaman.forms import MediaModelForm
from taggit.forms import TagField

from gallery.models import Gallery


class MediaForm(MediaModelForm):
    """
    Subclass of :class:`mediaman.forms.MediaModelForm` that makes the following changes:
    
        * Exclude the creator and created classes.
        * Add an optional delete field.

    This is used in the :func:`gallery.views.gallery_edit_metadata` as a formset, allowing the user to edit galleries in bulk.
    
    .. admonition:: Cover Images
    
        This class does *not* provide a field for selecting a gallery's cover image.  This is because that field is unique in the formset, not an individual form.  Instead this field is included as an radio button in the `gallery/templates/gallery/_media_form.html` template.
    """
    delete = forms.BooleanField(required=False)
    caption = forms.CharField(required=False)
    tags = TagField(required=False)

    class Meta:
        model = MediaUpload
        exclude = [
                "creator",
                "created",
                "media",
        ]
        
        
MediaFormSet =  modelformset_factory(
                    MediaUpload,
                    extra=0,
                    form=MediaForm
                )

class GalleryDetailsForm(forms.ModelForm):
    """
    Form for users to provide details for a :class:`gallery.models.Gallery`.  Also provides a :class:`forms.FileField` so that users can upload a zip archive of photos to attach to the gallery.
    
    Updates the labels for the *name* and *description* fields.
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
