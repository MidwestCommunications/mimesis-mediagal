from django.test import TestCase
from django.template import Template, Context
from django import template

from mimesis.models import MediaUpload

class TemplateTagTest(TestCase):
    fixtures = ["templatetag_test"]

    def render_template(self, src, ctx):
        src = "{% load gallery_tags %} " + src
        return Template(src).render(ctx)


    def test_render_image(self):
        
        image = MediaUpload.objects.get()
        c = Context({"image": image})
        t = "{% render_media image %}"

        rendered = self.render_template(t, c)

        self.assertTrue('<div id="image_1"' in rendered)

        self.assertTrue("Created by testor on" in rendered)

        self.assertTrue('<div id="image_1_content">' in rendered)

        self.assertTrue('<div id="image_1_caption">' in rendered)