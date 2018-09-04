from django.contrib.sitemaps import Sitemap

from cdhweb.blog.models import BlogPost


class BlogPostSitemap(Sitemap):

    def items(self):
        return BlogPost.objects.published()

    # location uses get_absolute_url by default

    def lastmod(self, item):
        return item.updated or item.published
