from django.contrib.sitemaps import Sitemap
from django.core.exceptions import ObjectDoesNotExist

from mezzanine.pages.models import Page


class PublishedItemSitemap(Sitemap):
    '''Generic sitemap with common logic for displayable models'''

    #: django model to use for items
    model = None

    def items(self):
        return self.model.objects.published()

    # location uses get_absolute_url by default

    def lastmod(self, item):
        return item.updated or item.published


class PageSitemap(PublishedItemSitemap):
    '''Sitemap for pages; includes rich text pages and landing pages'''
    model = Page

    def items(self):
        return super().items().filter(in_sitemap=True)

    def priority(self, item):
        # set landing pages at slightly higher priority
        try:
            if item.landingpage:
                return 0.6
        except ObjectDoesNotExist:
            # default priority is 0.5
            return

