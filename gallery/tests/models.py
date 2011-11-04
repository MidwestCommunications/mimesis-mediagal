from django.test import TestCase

from django.contrib.auth.models import User

from gallery.models import Gallery

class TestModels(TestCase):
    
    def setUp(self):
        self.user = User(username="tester", password="test")
        self.user.save()

    def tearDown(self):
        pass
    
    def test_creating_gallery(self):
        g = Gallery(name="My gallery", owner=self.user)
        self.assertEqual("My gallery", g.name)
