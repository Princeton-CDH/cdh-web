from cdhweb.blog.models import BlogPost
from cdhweb.resources.sitemaps import PublishedItemSitemap


class BlogPostSitemap(PublishedItemSitemap):
    model = BlogPost
