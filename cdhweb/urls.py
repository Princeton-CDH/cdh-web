from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView, TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps import Sitemap
from wagtail.contrib.sitemaps import views as sitemap_views
from wagtail.core import urls as wagtail_urls
from wagtail.core.models import Page
from wagtail.documents import urls as wagtaildocs_urls

from cdhweb.blog.sitemaps import BlogListSitemap
from cdhweb.events.sitemaps import EventListSitemap
from cdhweb.pages.views import SiteSearchView
from cdhweb.people.sitemaps import PeopleListSitemap
from cdhweb.projects.sitemaps import ProjectListSitemap

admin.autodiscover()

# use test favicon when test warning is enabled as another visual indicator
FAVICON = "/static/favicon.ico"
if getattr(settings, "SHOW_TEST_WARNING", False):
    FAVICON = "/static/favicon-test.ico"

# sitemap configuration for sections of the site
sitemaps = {
    "pages": Sitemap,  # wagtail content pages
    "people": PeopleListSitemap,
    "projects": ProjectListSitemap,
    "events": EventListSitemap,
    "blog": BlogListSitemap,
}


urlpatterns = [
    # admin site
    path("admin/", admin.site.urls),
    # special paths
    re_path(
        r"^robots\.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    re_path(r"^favicon\.ico$", RedirectView.as_view(url=FAVICON, permanent=True)),
    path("500/", lambda _: 1 / 0),  # for testing 500 error page
    # main apps
    path("people/", include("cdhweb.people.urls", namespace="people")),
    path("updates/", include("cdhweb.blog.urls", namespace="blog")),
    path("events/", include("cdhweb.events.urls", namespace="event")),
    path("projects/", include("cdhweb.projects.urls", namespace="projects")),
    # search
    path("search/", SiteSearchView.as_view(), name="search"),
    # CAS login urls
    path("accounts/", include("pucas.cas_urls")),
    # - all blog urls are now under updates/
    re_path(
        r"^blog(?P<blog_url>.*)$",
        RedirectView.as_view(url="/updates%(blog_url)s", permanent=True),
    ),
    # sitemaps
    path(
        "sitemap.xml", sitemap_views.index, {"sitemaps": sitemaps}, name="sitemap-index"
    ),
    re_path(
        r"^sitemap-(?P<section>.+)\.xml$",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # wagtail paths
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # let wagtail handle everything else
    path("", include(wagtail_urls)),
]

if settings.DEBUG:

    # serve static files in development - automatically activates in DEBUG; see
    # https://docs.djangoproject.com/en/3.1/howto/static-files/#serving-files-uploaded-by-a-user-during-development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar

        # must come before wagtail catch-all route or else debug urls 404
        urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))
    except ImportError:
        pass
