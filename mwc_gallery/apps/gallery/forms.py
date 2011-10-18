"""
=====
Forms
=====

Forms for the MWC Gallery app.
"""
from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from mimesis.models import MediaUpload
from mediaman.forms import MediaModelForm

from apps.gallery.models import Gallery


class MediaForm(MediaModelForm):
    """
    Subclass of :class:`mediaman.forms.MediaModelForm` that makes the following changes:
    
        * Change the widget for the *creator* field to :class:`django.forms.HiddenInput`.
        * Change the lable of the *caption* field.
    
    This is returned in the :func:`apps.gallery.views.gallery_images_uploaded`, and then POSTed to :func:`apps.gallery.views.gallery_edit_details`,
    normally as a formset.
    """
    
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
        
MediaFormSet =  modelformset_factory(
                    MediaUpload,
                    extra=0,
                    exclude = [
                        "creator",
                        "created",
                    ]
                )
MediaFormSet.__doc__ = """
Formset that allows end users to modify :class:`mimesis.models.MediaUpload` instances in bulk.

Excludes the `creator` and `created` fields.  Does not create an extra form for adding a new instance.
"""

class GalleryDetailsForm(forms.ModelForm):
    """
    Form for users to provide details for a :class:`apps.gallery.models.Gallery`.  Also provides a :class:`forms.FileField` so that users can upload a zip archive of photos to attach to the gallery.
    
    Updates the labels for the *name* and *description* fields.
    """
    photos = forms.FileField()

    class Meta:
        model = Gallery
        fields = [
                "name",
                "description",
                "tags",
        ]
        
    def __init__(self, *args, **kwargs):
        super(GalleryDetailsForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = "Gallery Name"
        self.fields["description"].label = "Gallery Description"
        self.fields["photos"].label = "Photos (zip file)"
