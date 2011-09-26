"""
This middleware takes the session identifier in a POST message and adds it to
the cookies instead.

This is necessary because SWFUpload won't send proper cookies back; instead,
all the cookies are added to the form that gets POST-ed back to us.

Slightly modified from
http://blog.fogtunes.com/2009/11/howto-integrate-swfupload-with-django/
"""

from django.conf import settings
from django.core.urlresolvers import reverse


class SWFUploadMiddleware(object):

    def process_request(self, request):
        
        if ((request.method == 'POST') and
            (request.path == reverse('gallery_resource_upload')) and
            settings.SESSION_COOKIE_NAME in request.POST):
            request.COOKIES[settings.SESSION_COOKIE_NAME] = request.POST[settings.SESSION_COOKIE_NAME]
        if "csrftoken" in request.POST:
            request.COOKIES["csrftoken"] = request.POST["csrftoken"]
             