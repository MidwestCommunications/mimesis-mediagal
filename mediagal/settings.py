"""
========
Settings
========

This file defines the following settings for the gallery application:
    
    * THUMBNAIL_SIZES: A dictionary that defines human-readable names for thumnail sizes.  Names in this dictionary can be whatever you like, and they will be used to generate filenames for the thumbnails.  The format for the ratio tuple is `(width, height)` in pixels.  The default dictionary looks like this::
        
        {
         "small": (80,80),
         "medium": (120,120),
         "large": (160,160)
        }
    * THUMBNAIL_ROOT: Path that thumnails will be saved to, relative to `MEDIA_ROOT`.  The default is `thumbs`

    
"""

from os import path
from django.conf import settings

# Define a default dictionary with image ratios.
# Ratios are (width, height)
THUMBNAIL_SIZES = settings.THUMBNAIL_SIZES = getattr(
                                                settings, 
                                                "THUMBNAIL_SIZES", 
                                                {
                                                    "small": (80,80),
                                                    "medium": (120,120),
                                                    "large": (160,160)
                                                }
                                            )

THUMBNAIL_ROOT = settings.THUMBNAIL_ROOT = getattr(settings, "THUMBNAIL_ROOT", "thumbs")
