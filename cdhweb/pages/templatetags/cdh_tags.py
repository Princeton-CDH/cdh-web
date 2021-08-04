from collections import OrderedDict

from django import template
from django.conf import settings

from cdhweb.pages.utils import absolutize_url

register = template.Library()

#: mapping from url portion to CDH icon name; ordered to ensure more specific
#: options are checked first.
URL_ICON_MAPPING = OrderedDict(
    [
        ("/people/", "ppl"),
        ("/projects", "folder"),
        ("reading", "book"),
        ("/events/", "cal"),
        ("/contact/", "convo"),
        ("/consult/", "convo"),
        ("seed-grant", "seed"),
        ("travel", "location"),
        ("fellowship", "medal"),
        ("prize", "medal"),
        ("grant", "grant"),
        ("funding", "grant"),
        ("year", "cal"),
    ]
)


@register.filter
def url_to_icon(value):
    """Return an appropriate CDH icon name based on URL."""
    if not value:
        return ""
    for url, icon in URL_ICON_MAPPING.items():
        if url in value:
            return icon
    return ""


@register.filter
def url_to_icon_path(value):
    """Return absolute path to CDH icon name based on URL."""
    img = url_to_icon(value)
    if img:
        return absolutize_url(
            "{}img/cdh-icons/png@2X/{}@2x.png".format(settings.STATIC_URL, img)
        )
    return ""


@register.filter("startswith")
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    """Add or replace a single GET parameter in a URL."""
    # Adapted from https://stackoverflow.com/questions/5755150/altering-one-query-parameter-in-a-url-django
    params = context["request"].GET.copy()
    params[field] = value
    return params.urlencode()
