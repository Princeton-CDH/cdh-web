from django import template

register = template.Library()


@register.filter
def url_to_icon(value):
    '''Return appropriate CDH icon name based on URL.'''
    if '/people/' in value:
        return 'people'
    if '/projects/' in value:
        return 'folder'
    if '/events/' in value:
        return 'cal'
    if '/contact/' in value:
        return 'convo'
    if 'seed-grant' in value:
        return 'seed'
    if 'fellowship' in value or 'prize' in value:
        return 'medal'
    if 'grants' in value or 'funding' in value:
        return 'grant'

    return ''
