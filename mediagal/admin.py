from django.contrib import admin

from mediagal.models import Gallery, GalleryMedia, GallerySites

class GalleryMediaInline(admin.TabularInline):
    model = GalleryMedia
    
    
class GallerySitesInline(admin.StackedInline):
    model = GallerySites
    
    
class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryMediaInline, GallerySitesInline]
    

admin.site.register(Gallery, GalleryAdmin)
