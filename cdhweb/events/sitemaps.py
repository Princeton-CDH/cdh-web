from cdhweb.events.models import Event
from cdhweb.resources.sitemaps import PublishedItemSitemap


class EventSitemap(PublishedItemSitemap):
    model = Event