from cdhweb.projects.models import Project
from cdhweb.resources.sitemaps import PublishedItemSitemap


class ProjectSitemap(PublishedItemSitemap):
    model = Project

    def priority(self, item):
        priority = 0.5
        # projects built by cdh should be higher priority
        if item.cdh_built:
            priority += 0.1
        # projects with live website should be higher priority
        if item.website_url:
            priority += 0.1
        # (projects built by cdh with live website will be highest priority)
        return priority
