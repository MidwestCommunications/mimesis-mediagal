from django.db import models

from taggit.managers import TaggableManager

from mimesis.managers import WithMediaManager


class Something(models.Model):
    name = models.CharField(max_length=100)
    tags = TaggableManager(blank=True)
    
    objects = models.Manager()
    with_media = WithMediaManager()
    
    def __unicode__(self):
        return self.name
