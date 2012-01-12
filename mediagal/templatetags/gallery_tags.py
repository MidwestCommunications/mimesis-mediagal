"""
=============
Template Tags
=============

The template tags registered for the gallery application.
"""
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django import template

from mimesis.models import MediaUpload

register = template.Library()


class MediaUploadNode(template.Node):
    """
    Takes a context variable name and uses it's mimetype and other metadata
    to populate an HTML subtemplate.
    
    This was written with :class:`mimesis.models.MediaUpload` in mind, but could implement
    anything with matching attributes.
    
    Templates called by this include the following:

        * templates/mediagal/_base_display.html - The base template that all subtemplates should extend
        * templates/mediagal/_(typename)_display.html - Template matching your object's ``media_type`` attribute.  For exmaple, "_image_display.html" would be used for images, "_video_display.html" for videos.

    **Context Variables**:
    
        * id: The primary key for the passed in object.
        * caption: Caption provided by the object.
        * thumb: Thumbnail URL
        * media_item: The actual media that is wrapped by the model.
        * media_type: Type of the media, i.e. :mimetype:`photo`.
        * media_subtype: Subtype of media, i.e. :mimetype:`jpg`
        * creator: Primary key for the user who created this model.
        * created: Date and time the media was created.
        * tags: QuerySet for all the tags associated with the media
        * Also, any context passed into the parent templates will be available. The default image template relies on this fact.

    .. admonition:: Improvements
    
        * The ``tags`` variable should take an existing QuerySet, rather than make the call itself.
    """
    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        var = context[self.var_name]
        type_ = var.media_type
        t_name = "mediagal/mime/_%s_display.html" % type_
        template = get_template(t_name)
        c = Context({
            "id": var.pk,
            "caption": var.caption,
            "thumb": var.thumbnail_img_url,
            "media_item": var.media,
            "media_type": var.media_type,
            "media_subtype": var.media_subtype,
            "creator": var.creator,
            "created": var.created,
            "tags": var.tags.all(),
        })
        c.update(context)
        return template.render(c)
        
        
def do_render_media(parser, token):
    """
    Parses the tag to separate the tag name and the variable that it was passed.
    
    Usage::
        
        {% render_media media_upload %}
        
    See the :class:`MediaUploadNode` class for more details on actual behavior of the tag.

    """
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r requires a single argument" % token.contents.split()[0])
        
    return MediaUploadNode(var_name)
    
    
register.tag("render_media", do_render_media)


# {% render_media media_upload %}

# What it needs to do:
#   Take the media upload *object*
#   Extract:
#       Media type (for choosing the template)
#       Caption
#       Value (links, image url, etc)
#       Creator (?)
#       Creation Date (?)
#   Those go into a dictionary that gets passed to the sub template
#   Subtemplate name generated with the media type?
