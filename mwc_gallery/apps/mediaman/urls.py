from django.conf.urls.defaults import *

urlpatterns = patterns('mediaman.views',
    
    url(r'^mediaselector/$',
        'media_selector',
        name='mediaman_media_selector',
    ),
    
    url(r'^mediaselector/search/$',
        'media_selector_search',
        name='mediaman_media_selector_search',
    ),
    
    url(r'^mediaselector/upload/$',
        'media_selector_upload',
        name='mediaman_media_selector_upload',
    ),
    
    url(r'^mediaselector/preview/(\d+)/$',
        'media_selector_preview',
        name='mediaman_media_selector_preview',
    ),
    
    url(r'^mediaselector/edit/(\d+)/$',
        'media_selector_edit',
        name='mediaman_media_selector_edit',
    ),
    
    url(r'^filter_tags/$', 
        'filter_tags',
        name='mediaman_filter_tags',
    ),

)

