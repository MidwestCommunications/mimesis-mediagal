from django.test import TestCase
from django.forms import ModelForm
from django.contrib.auth.models import User

from mediaman.tests.exampleapp.models import Something
from mediaman.tests.exampleapp.forms import SomethingForm

from mimesis.models import MediaUpload, MediaAssociation
from mediaman.forms import TagField


class TagFieldTests(TestCase):
    def test_no_commas(self):
        class TestForm(ModelForm):
            tags = TagField()
            class Meta:
                model = Something
        something = Something.objects.create(name='thing')
        something.tags.add('herp', 'derp', 'yerp')
        form = TestForm(instance=something)
        self.assertFalse(',' in str(form))


class MediaFormTests(TestCase):
    
    def test_normal_operation(self):
        """Form should save an object normally with no media."""
        
        # create with form, save immediately
        form = SomethingForm({'name': 'thing'})
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.name, 'thing')
        self.assertRaises(AttributeError, lambda:form.save_mimesis_media)
        
        # create with form, save later
        form = SomethingForm({'name': 'thing'})
        obj = form.save(False)
        self.assertFalse(obj.pk)
        obj.save()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.name, 'thing')
        form.save_mimesis_media()
        
        # edit existing object, save immediately
        obj = Something.objects.create(name='thing')
        form = SomethingForm(instance=obj)
        self.assertFalse(form.is_valid())
        form = SomethingForm({'name': 'edited'}, instance=obj)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.name, 'edited')
        self.assertRaises(AttributeError, lambda:form.save_mimesis_media)
        
        # edit existing object, save later
        obj = Something.objects.create(name='thing')
        form = SomethingForm({'name': 'edited'}, instance=obj)
        self.assertTrue(form.is_valid())
        form.save(False)
        obj.save()
        form.save_mimesis_media()
    
    def test_attach_media(self):
        """Form should save properly with media attached."""
        
        user = User.objects.create_user('user', 'mail@mail.com')
        media = [
            MediaUpload.objects.create(
                caption='media%s' % (i + 1),
                media='blah',
                creator=user
            )
            for i in range(2)
        ]
        pks = ','.join([str(m.pk) for m in media])
        
        # create with form, save immediately
        form = SomethingForm({'name': 'thing', 'mimesis_attached_media': pks})
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.name, 'thing')
        self.assertRaises(AttributeError, lambda:form.save_mimesis_media)
        obj_assocs = MediaAssociation.objects.for_model(obj)
        self.assertEqual(len(obj_assocs), len(media))
        self.assertTrue(all(ma.media in media for ma in obj_assocs))
        
        # create with form, save later
        form = SomethingForm({'name': 'thing', 'mimesis_attached_media': pks})
        obj = form.save(False)
        self.assertFalse(obj.pk)
        obj.save()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.name, 'thing')
        form.save_mimesis_media()
        obj_assocs = MediaAssociation.objects.for_model(obj)
        self.assertEqual(len(obj_assocs), len(media))
        self.assertTrue(all(ma.media in media for ma in obj_assocs))
        
        # edit existing object, save immediately
        obj = Something.objects.create(name='thing')
        form = SomethingForm(instance=obj)
        self.assertFalse(form.is_valid())
        form = SomethingForm({'name': 'edited', 'mimesis_attached_media': pks}, instance=obj)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.name, 'edited')
        self.assertRaises(AttributeError, lambda:form.save_mimesis_media)
        obj_assocs = MediaAssociation.objects.for_model(obj)
        self.assertEqual(len(obj_assocs), len(media))
        self.assertTrue(all(ma.media in media for ma in obj_assocs))
        
        # edit existing object, save later
        obj = Something.objects.create(name='thing')
        form = SomethingForm({'name': 'edited', 'mimesis_attached_media': pks}, instance=obj)
        self.assertTrue(form.is_valid())
        form.save(False)
        obj.save()
        form.save_mimesis_media()
        obj_assocs = MediaAssociation.objects.for_model(obj)
        self.assertEqual(len(obj_assocs), len(media))
        self.assertTrue(all(ma.media in media for ma in obj_assocs))
    
    def test_detach_media(self):
        """Form should remove already-attached media."""
        
        user = User.objects.create_user('user', 'mail@mail.com')
        media = [
            MediaUpload.objects.create(
                caption='media%s' % (i + 1),
                media='blah',
                creator=user
            )
            for i in range(2)
        ]
        pks = ','.join([str(m.pk) for m in media])
        media1 = media[0]
        obj = SomethingForm({'name': 'thing', 'mimesis_attached_media': pks}).save()
        SomethingForm({'name': 'edited', 'mimesis_attached_media': str(media1.pk)}, instance=obj).save()
        obj_assocs = MediaAssociation.objects.for_model(obj)
        self.assertEqual(len(obj_assocs), 1)
        self.assertEqual(obj_assocs[0].media, media1)


__all__ = ['TagFieldTests', 'MediaFormTests']
