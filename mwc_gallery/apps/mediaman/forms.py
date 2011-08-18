import re

from django.forms import ModelForm, CharField, TextInput, Textarea, HiddenInput, ValidationError
from django.forms.util import ErrorList
from django.contrib.contenttypes.models import ContentType

from mimesis.models import MediaUpload, MediaAssociation
from taggit.utils import parse_tags


class TagWidget(TextInput):
    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, basestring):
            value = ' '.join(sorted([o.tag.name for o in value.select_related("tag")]))
        return super(TagWidget, self).render(name, value, attrs)


class TagField(CharField):
    
    widget = TagWidget
    
    def clean(self, value):
        try:
            # only accept letters, digits, and spaces
            if re.search(r'[^a-zA-Z0-9 ]', value) is not None:
                raise ValueError
            return parse_tags(value.lower())
        except ValueError:
            raise ValidationError('Please provide a space-separated list of tags.')


class MetadataForm(ModelForm):
    
    caption = CharField(widget=Textarea, max_length=500)
    tags = TagField(help_text='Separate tags with spaces.')
    
    class Meta:
        model = MediaUpload
        fields = ('caption', 'tags')


class MediaModelForm(ModelForm):
    
    mimesis_attached_media = CharField(required=False, widget=HiddenInput())
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
            initial=None, error_class=ErrorList, label_suffix=':',
            empty_permitted=False, instance=None):
        if instance:
            initial = initial or {}
            initial_media = ','.join([str(pk) for pk in MediaAssociation.objects.for_model(instance).values_list('media_id', flat=True)])
            initial['mimesis_attached_media'] = initial_media
        super(MediaModelForm, self).__init__(data, files, auto_id, prefix,
            initial, error_class, label_suffix, empty_permitted, instance)
    
    def save(self, commit=True):
        instance = super(MediaModelForm, self).save(commit=commit)
        # create a function to save attached media for when commit=False
        # this idea is taken from Django ModelForm's save_m2m functionality
        def save_mimesis_media():
            to_attach = self.cleaned_data['mimesis_attached_media'].split(',')
            if to_attach[0]:
                primary_id = int(to_attach[0])
                to_attach = set([int(id) for id in to_attach])
            else:
                primary_id = None
                to_attach = set()
            current = set(MediaAssociation.objects.for_model(instance).values_list('media_id', flat=True))
            to_del = MediaAssociation.objects.filter(
                content_type=ContentType.objects.get_for_model(instance),
                object_pk=instance.pk,
                media__in=(current - to_attach)
            ).delete()
            MediaAssociation.objects.for_model(instance).filter(is_primary=True).update(is_primary=False)
            for media in MediaUpload.objects.filter(id__in=(to_attach - current)):
                MediaAssociation.objects.create(
                    media=media,
                    content_object=instance,
                    is_primary=(media.id == primary_id)
                )
            if primary_id in current:
                MediaAssociation.objects.for_model(instance).filter(media__id=primary_id).update(is_primary=True)
        if commit:
            save_mimesis_media()
        else:
            self.save_mimesis_media = save_mimesis_media
        return instance
    
    save.alters_data = True
