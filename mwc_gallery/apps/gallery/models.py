import datetime


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
    
    photos = models.ManyToManyField(MediaUpload, related_name="galleries")
    
    def __unicode__(self):
        return self.name

class GalleryAssociation(models.Model):
    
    gallery = models.ForeignKey(Gallery)
    description = models.TextField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()


