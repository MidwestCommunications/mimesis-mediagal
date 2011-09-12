from django.template import Context
from django.template.loader import get_template
from django import template

from mimesis.models import MediaUpload

register = template.Library()

class MediaUploadNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, context):
        var = context[self.var_name]
        type = var.media_type
        t_name = "gallery/_%s_display.html" % type
        template = get_template(t_name)
        c = Context({
            "caption": var.caption,
            "thumb": var.thumbnail_img_url,
            "media": var.media,
            "creator": var.creator,
            "created": var.created,
            "tags": var.tags.all(),
        })
        return template.render(c)


def do_media_upload_subtemplate(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r requires a single argument" % token.contents.split()[0])
    
    return MediaUploadNode(var_name)



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
