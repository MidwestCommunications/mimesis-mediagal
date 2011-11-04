import re

from taggit.models import Tag


def tags_from_string(phrase):
    ignore_list = ['a', 'an', 'as', 'at', 'before', 'but', 'by', 'for', 'from',
        'is', 'in', 'into', 'like', 'of', 'off', 'on', 'onto', 'per', 'since',
        'than', 'the', 'this', 'that', 'to', 'up', 'via', 'with']
    word_list = re.findall(r'[A-Za-z0-9]+', phrase.lower())
    word_list = [word for word in word_list if word not in ignore_list]
    return Tag.objects.filter(name__in=word_list).values_list('name', flat=True)


def auto_tag_objects(obj_list, from_field, tag_field='tags'):
    for obj in obj_list:
        tag_list = tags_from_string(getattr(obj, from_field, ''))
        getattr(obj, tag_field).add(*tag_list)
