from django.test import TestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User


class MediaSelectorTests(TestCase):
    def test_youtube_urls(self):
        User.objects.create_user('user', 'mail@mail.com', 'pass')
        self.client.login(username='user', password='pass')
        
        url_ids = [
            ('http://www.youtube.com/watch?v=FxEjHc-tLWc&feature=feedrec_grec_index', 'FxEjHc-tLWc'),
            ('http://www.youtube.com/watch?v=qo_RRk_KjaE', 'qo_RRk_KjaE'),
            ('http://www.youtube.com/watch?v=sudk3ZdMsVA&feature=featured', 'sudk3ZdMsVA'),
        ]
        for (url, video_id) in url_ids:
            r = self.client.post(reverse('mediaman_media_selector_upload'), {'mediaman-embed-url': url})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.context['media_item'].media.name, video_id)
        
        bad_urls = [
            '',
        ]
        for url in bad_urls:
            r = self.client.post(reverse('mediaman_media_selector_upload'), {'mediaman-embed-url': url})
            self.assertEqual(r.status_code, 400)


__all__ = ['MediaSelectorTests']
