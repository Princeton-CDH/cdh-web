from collections import OrderedDict

from django import template
from django.conf import settings

from cdhweb.resources.utils import absolutize_url

register = template.Library()

#: mapping from url portion to CDH icon name; ordered to ensure more specific
#: options are checked first.
URL_ICON_MAPPING = OrderedDict([
    ('/people/', 'ppl'),
    ('/projects/', 'folder'),
    ('/events/', 'cal'),
    ('/contact/', 'convo'),
    ('seed-grant', 'seed'),
    ('fellowship', 'medal'),
    ('prize', 'medal'),
    ('grant', 'grant'),
    ('funding', 'grant')
])



@register.filter
def url_to_icon(value):
    '''Return an appropriate CDH icon name based on URL.'''
    for url, icon in URL_ICON_MAPPING.items():
        if url in value:
            return icon
    return ''

@register.filter
def url_to_icon_path(value):
    '''Return absolute path to CDH icon name based on URL.'''
    img = url_to_icon(value)
    if img:
        return absolutize_url('{}img/cdh-icons/{}.svg'.format(settings.STATIC_URL, img))
    return ''
