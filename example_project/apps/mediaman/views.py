import re

from django.http import HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Q, Count

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required

from mimesis.models import MediaUpload, MediaAssociation
from taggit.models import TaggedItem

from mediaman.forms import MetadataForm
from mediaman.utils import tags_from_string


MEDIA_LIST_LIMIT = 20


def _filter_media(media_type=None, for_model=None, search_tags=None, limit=MEDIA_LIST_LIMIT):
    media_list = MediaUpload.objects.all()
    if media_type:
        if media_type == 'other':
            media_list = media_list.exclude(media_type__in=['image', 'video', 'audio'])
        else:
            media_list = media_list.filter(media_type=media_type)
    if for_model:
        (app_label, model_name) = for_model.split('.')
        ct = ContentType.objects.get(app_label=app_label, model=model_name)
        media_list = media_list.filter(mediaassociation__content_type=ct)
    if search_tags:
        tagged_ids = TaggedItem.objects.filter(
            tag__name__in=search_tags.lower().split(),
            content_type=ContentType.objects.get_for_model(MediaUpload),
            object_id__in=media_list.values_list('id', flat=True)
        ).values('object_id').annotate(num=Count('pk')).order_by('-num')[:limit]
        media_ids = [item['object_id'] for item in tagged_ids]
        media_uploads = MediaUpload.objects.annotate(attachments=Count('mediaassociation')).in_bulk(media_ids)
        media_list = [media_uploads[media_id] for media_id in media_ids]
    else:
        media_list = media_list.annotate(attachments=Count('mediaassociation'))
    return media_list


def media_selector(request):
    for_model = request.GET.get('model')
    attached_ids = request.GET.get('media')
    search_tags = request.GET.get('searchtags', '')
    
    media_list = _filter_media('image', for_model, search_tags)
    
    attached_media = []
    if attached_ids:
        attached_ids_list = [int(aid) for aid in attached_ids.split(',')]
        attached_dict = MediaUpload.objects.in_bulk(attached_ids_list)
        attached_media = [attached_dict[aid] for aid in attached_ids_list]
    
    return render_to_response('mediaman/media-selector.html', {
        'for_model': for_model,
        'attached_to': 'any',
        'media_type': 'image',
        'media_list': media_list[:MEDIA_LIST_LIMIT],
        'attached_media': attached_media,
        'search_tags': search_tags
    }, context_instance=RequestContext(request))


def media_selector_search(request):
    for_model = request.GET.get('model')
    media_type = request.GET.get('mediatype')
    attached_to = request.GET.get('attachedto')
    search_tags = request.GET.get('searchtags', '')
    
    if attached_to != 'this':
        for_model = None
    media_list = _filter_media(media_type, for_model, search_tags)
    
    return render_to_response(
        'mediaman/list.html',
        {'media_list': media_list[:MEDIA_LIST_LIMIT]},
        RequestContext(request)
    )


@login_required
def media_selector_upload(request):
    if request.method == 'POST':
        if request.FILES:
            media = request.FILES['mediaman-upload-file']
            (media_type, media_subtype) = (None, None)
        else:
            url = request.POST.get('mediaman-embed-url')
            # extract the YouTube video ID
            matched = re.search(r'(?<=v=)[a-zA-Z0-9_-]+', url)
            if matched:
                media = matched.group(0)
                (media_type, media_subtype) = ('video', 'youtube')
            else:
                media = None
        if media:
            media_upload = MediaUpload.objects.create(
                media=media,
                creator=request.user,
                media_type=media_type,
                media_subtype=media_subtype
            )
            return render_to_response(
                'mediaman/list-item.html',
                {'media_item': media_upload},
                RequestContext(request)
            )
        return HttpResponseBadRequest()
    media_list = MediaUpload.objects.filter(creator=request.user) \
        .order_by('-created').annotate(attachments=Count('mediaassociation'))
    return render_to_response(
        'mediaman/upload.html',
        {'media_list': media_list[:MEDIA_LIST_LIMIT]},
        context_instance=RequestContext(request)
    )


def media_selector_preview(request, media_id):
    media_item = get_object_or_404(MediaUpload, pk=media_id)
    return render_to_response('mediaman/preview.html', {
        'media_item': media_item
    }, context_instance=RequestContext(request))


@login_required
def media_selector_edit(request, media_id):
    media_item = get_object_or_404(MediaUpload, pk=media_id)
    if media_item.mediaassociation_set.count():
        return HttpResponseBadRequest('Media has already been attached.')
    if request.method == 'POST':
        form = MetadataForm(request.POST, instance=media_item, prefix='mediaman')
        if form.is_valid():
            media_item = form.save()
            return render_to_response('mediaman/list-item.html', {
                'media_item': media_item
            }, context_instance=RequestContext(request))
    else:
        form = MetadataForm(instance=media_item, prefix='mediaman')
    return render_to_response('mediaman/edit.html', {
        'media_item': media_item,
        'form': form
    }, context_instance=RequestContext(request))


def filter_tags(request):
    found_list = tags_from_string(request.GET.get('s'))
    return HttpResponse(' '.join(found_list), content_type='text/plain')
