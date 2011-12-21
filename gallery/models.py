"""
======
Models
======

Models used within the Gallery app.  The main model class is the :class:`Gallery`, which associates many :class:`mimesis.models.MediaUpload` objects together into a common "container".
"""

import datetime
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from mimesis.models import MediaUpload
from taggit.managers import TaggableManager

from gallery.thumbnails import generate_all_thumbnails


class Gallery(models.Model):
    """
    A gallery that has the following:
    
        * A name (max length 50 chars)
        * A description (optional)
        * An owner (Foreign key to :class:`django.contrib.auth.models.User`)
        * Creation date/time
        * ManyToManyField to :class:`mimesis.models.MediaUpload`, through a :class:`GalleryMedia` obejct
        * Cover image, a ForeignKey to :class:`mimesis.models.MediaUpload` that will appear as the thumbnail for the gallery.
        * Sites, a ManyToManyField to :class:`django.contrib.sites.models.Site`.
        
    """
    
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(default=datetime.datetime.now)
    
    tags = TaggableManager()
    
    media = models.ManyToManyField(
            MediaUpload,
            related_name="galleries",
            through="GalleryMedia"
    )
    cover = models.ForeignKey(MediaUpload, null=True) # Nullable for backwards compat.
    sites = models.ManyToManyField(Site, through="GallerySites", null=True) # Nullable for backwards compat.
    
    def __unicode__(self):
        return self.name
        
        
    def get_absolute_url(self):
        return reverse("gallery_details", args=(self.pk,))
        
        
    class Meta:
        verbose_name_plural = "Galleries"
        ordering = ["-updated"]
        
        
    def delete(self):
        """
        Remove the association between the gallery and it's media.
        """
        GalleryMedia.objects.filter(gallery=self).delete()
        super(Gallery, self).delete()
        
        
    def add_media(self, media_upload):
        """
        Associates a :class:`mimesis.MediaUpload` object with this gallery.
        """
        self.updated = datetime.datetime.now()
        self.save()
        return GalleryMedia.objects.create(
                gallery=self,
                media=media_upload
        )
        
        
    def add_site(self, site):
        """
        Associates a :class:`django.contrib.sites.models.Site` object with this gallery.
        """
        obj, created =  GallerySites.objects.get_or_create(
            gallery=self,
            site=site
        )
        return obj
        
    def from_zip(self, zip_file, initial=False):
        """
        Populates a gallery with photos within a zip archive.
        
        When a zip archive comes in, it is first checked for corrupt files.
        If nothing's corrupted, it's contents are unpacked into MEDIA_ROOT, and an
        associated :class:`mimesis.MediaUpload` model/file are created and bound to the gallery.  Once that is finished, the file in MEDIA_ROOT is deleted.
        
        If the `initial` argument is True, then this function will set the gallery's cover image to the first file extracted from the archive.
        
        Most of this function is based on Photologue's GalleryUpload.process_zipefile method, changed to use the :class:`mimesis.MediaUpload` models.
        """
        zip = zipfile.ZipFile(zip_file)
        bad_file = zip.testzip()
        if bad_file:
            raise Exception("'%s' in the zip file is corrupt." % bad_file)
            
        if initial:
            default = None
            
        for filename in zip.namelist():
            if filename.startswith("__"):  # skip meta files.
                continue
                
            data = zip.read(filename)
            
            
            if len(data):
                file = SimpleUploadedFile(filename, data)
                media_upload = MediaUpload.objects.create(
                        creator=self.owner,
                        caption="",
                        media=file
                )
                media_upload.save()
                
                # Capture the first image to be used as the default cover image.
                if initial and not default:
                    default = media_upload
                    
                self.add_media(media_upload)
                
                generate_all_thumbnails(media_upload.media)
                
        zip.close()
        if initial:
            self.cover = default
            self.save()
            
            
    def remove_media(self, media):
        """
        Removes the association between a MediaUpload instance and this gallery.
        """
        try:
            m = self.media.get(id=media.id)
            GalleryMedia.objects.filter(
                gallery=self,
                media=m
            ).delete()
        except Exception:
            deleted = False
        else:
            deleted = True
        return deleted
        
        
class GalleryMedia(models.Model):
    """
    A 'pass through' model for ManyToMany relationsips between :class:`Gallery` and :class:`mimesis.models.MediaUpload` objects.
    """
    gallery = models.ForeignKey(Gallery)
    media = models.ForeignKey(MediaUpload)
    
    def __unicode__(self):
        return "<Gallery: %s, Media: %s>" % (self.gallery.name, self.media.caption)
        
        
    class Meta:
        verbose_name = "Gallery Media"
        verbose_name_plural = "Gallery Media"
        
        
class GallerySites(models.Model):
    """
    Pass through model to link :class:`Gallery` objects to :class:`django.contrib.sites.models.Site`.
    """
    gallery = models.ForeignKey(Gallery)
    site = models.ForeignKey(Site)
    
    def __unicode__(self):
        return "<Gallery: %s, Site: %s>" % (self.gallery.name, self.site.name)
        
    class Meta:
        verbose_name = "Gallery Sites"
        verbose_name_plural = "Gallery Sites"
        
        
class GalleryAssociation(models.Model):
    """
    Generic relationship between a gallery and any other Django model.

    Includes a description text field.
    """
    
    gallery = models.ForeignKey(Gallery)
    description = models.TextField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    
