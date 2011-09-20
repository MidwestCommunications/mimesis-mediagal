import datetime

from django.core.urlresolvers import reverse
from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from mimesis.models import MediaUpload

class Gallery(models.Model):
    
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    media = models.ManyToManyField(
            MediaUpload,
            related_name="galleries",
            through="GalleryMedia"
    )
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse("gallery_details", args=(self.pk,))

class GalleryMedia(models.Model):
    gallery = models.ForeignKey(Gallery)
    media = models.ForeignKey(MediaUpload)

class GalleryAssociation(models.Model):
    
    gallery = models.ForeignKey(Gallery)
    description = models.TextField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()


