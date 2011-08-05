import datetime


from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Gallery(models.Model):
    
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.name


class Photo(models.Model):
    
    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    gallery = models.ForeignKey(Gallery, related_name="photos")
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.title

class GalleryAssociation(models.Model):
    
    gallery = models.ForeignKey(Gallery)
    description = models.TextField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveintegerField()
    content_object = generic.GenericForeignKey()


