from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from django import template

from mimesis.models import MediaUpload

class TemplateTagTest(TestCase):
    fixtures = ["templatetag_test"]

    def render_template(self, src, ctx):
        src = "{% load gallery_tags %} " + src
        return Template(src).render(ctx)
        

    def test_render_image(self):
        
        image = MediaUpload.objects.get(pk=1)
        c = Context({"image": image, "gallery": image.galleries.all()[0]})
        t = "{% render_media image %}"

        rendered = self.render_template(t, c)
        
        self.assertTrue('<div id="image_1"' in rendered)
        
        self.assertTrue("Created by testor on" in rendered)
        
        self.assertTrue('<div id="image_1_content">' in rendered)

        self.assertTrue('<div id="image_1_caption">' in rendered)

    def test_missing_template(self):

        text_file = MediaUpload.objects.get(pk=2)
        c = Context({"file": text_file})
        t = "{% render_media file %}"
        self.assertRaises(TemplateSyntaxError, self.render_template, t, c)
