from cdhweb.people.models import Profile
from cdhweb.resources.sitemaps import PublishedItemSitemap


class ProfileSitemap(PublishedItemSitemap):
    model = Profile

    def items(self):
        # only published profiles with is_staff actually have detail pages
        # and should appear in the sitemap
        return super().items().filter(is_staff=True)
