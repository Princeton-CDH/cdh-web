import string
from datetime import timedelta

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from mezzanine.pages.models import Page
from mezzanine.core.models import CONTENT_STATUS_DRAFT
import pytest

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event, EventType
from cdhweb.projects.models import Project, GrantType, Grant
from cdhweb.resources.models import LandingPage
from cdhweb.resources.sitemaps import PageSitemap
from cdhweb.resources.utils import absolutize_url


class TestViews(TestCase):
    fixtures = ['test_pages.json']

    def test_site_index(self):
        index_url = reverse('home')

        # should not error even if no events/projects to display
        response = self.client.get(index_url)
        assert response.status_code == 200
        self.assertContains(response, "Next semester's events are being scheduled.",
            msg_prefix='should display a message when there are no upcoming events')
        self.assertContains(response, reverse('event:upcoming'),
            msg_prefix='should link to upcoming events (in lieue of an archive)')

        ### test the carousel display
        # shouldn't display without any blog posts
        self.assertTemplateNotUsed(response, 'snippets/carousel.html')
        # add some posts but don't feature any yet; should display most recent 3
        for n in range(1, 8):
            BlogPost.objects.create(title='Post %s' % n)
        response = self.client.get(index_url)
        assert len(response.context['updates']) == 3
        self.assertTemplateUsed(response, 'snippets/carousel.html')
        self.assertContains(response, '<div id="carousel')
        # one "active" slide, the rest are normal
        self.assertContains(response, '<div class="post-update active">', count=1)
        self.assertContains(response, '<div class="post-update">', count=2)
        # feature all of the posts; should display most recent 6
        for post in BlogPost.objects.all():
            post.is_featured = True
            post.save()
        response = self.client.get(index_url)
        assert len(response.context['updates']) == 6
        self.assertTemplateUsed(response, 'snippets/carousel.html')
        self.assertContains(response, '<div id="carousel')
        self.assertContains(response, '<div class="post-update active">', count=1)
        self.assertContains(response, '<div class="post-update">', count=5)

        # ensure all displayed posts have a title and link
        for post in BlogPost.objects.all()[:6]:
            self.assertContains(response, post.get_absolute_url())
            self.assertContains(response, post.title)

        ### test how projects are displayed on the home page
        today = timezone.now()
        site = Site.objects.first()
        projects = Project.objects.bulk_create(
            [Project(title='Meeting %s' % a, slug=a, highlight=True,
                     site=site, short_description='This is project %s' % a)
             for a in string.ascii_letters[:5]]
        )
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # add grant that covers the current date
        grant_start = today - timedelta(days=2)
        grant_end = today + timedelta(days=7)
        Grant.objects.bulk_create(
            [Grant(project=proj, grant_type=grtype,
                   start_date=grant_start, end_date=grant_end)
             for proj in Project.objects.all()]
        )

        response = self.client.get(index_url)
        # should be 4 random projects in context
        assert len(response.context['projects']) == 4

        # test that highlight flag is honored
        # - delete one project so that all four will be present
        Project.objects.first().delete()
        # get next project and mark not highlighted
        inactive_proj = Project.objects.first()
        inactive_proj.highlight = False
        inactive_proj.save()
        response = self.client.get(index_url)
        assert inactive_proj not in response.context['projects']

        # get next active project and remove grant
        noncurrent_proj = Project.objects.highlighted().first()
        noncurrent_proj.grant_set.all().delete()
        response = self.client.get(index_url)
        # highlight means it should be included even without grant
        assert noncurrent_proj in response.context['projects']
        # check that brief project details are displayed
        projects = Project.objects.highlighted()
        for proj in projects:
            self.assertContains(response, proj.get_absolute_url())
            self.assertContains(response, proj.title)
            self.assertContains(response, proj.short_description)
            # NOTE: currently not testing thumbnail included

        ### test how projects are displayed on the home page
        event_type = EventType.objects.first()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        past_event = Event.objects.create(start_time=yesterday,
            end_time=yesterday, event_type=event_type, title='Old News')
        Event.objects.bulk_create(
            [Event(start_time=tomorrow, end_time=tomorrow, title='event %s' % a,
                   slug=a, event_type=event_type, site=site)
             for a in string.ascii_letters[:5]]
        )

        response = self.client.get(index_url)
        # only three events in context
        assert len(response.context['events']) == 3
        # past event not displayed
        assert past_event not in response.context['events']
        self.assertContains(response, event_type, count=3)
        for event in Event.objects.published().upcoming()[:3]:
            self.assertContains(response, event.get_absolute_url())
            self.assertContains(response, event.title)
            # TODO: date/time

        # test editable page content displayed
        page = Page.objects.get(slug='/')
        self.assertContains(response, page.richtextpage.content)

        # TODO: not yet testing speakers displayed

        # not yet testing published/unpublished

    def test_child_pages_attachment(self):
        about = Page.objects.get(title='About')
        annual_report = Page.objects.get(title='Annual Report')
        response = self.client.get(about.get_absolute_url())
        # page-children attachment section should be present
        self.assertContains(response, '<div class="attachments page-children">')
        # child page title and url should be present
        self.assertContains(response, annual_report.title)
        self.assertContains(response, annual_report.get_absolute_url())

        # delete child page to check behavior without
        annual_report.delete()
        response = self.client.get(about.get_absolute_url())
        # should not error, should not contain page-children attachment section
        self.assertNotContains(response, '<div class="attachments page-children">')

    def test_sitemap(self):
        # basic test of sitemap url config, override from mezzanine
        response = self.client.get(reverse('sitemap'))
        assert response.status_code == 200

        # both fixture items are published
        for page in Page.objects.all():
            self.assertContains(response, page.get_absolute_url())
            self.assertContains(response, page.updated.strftime('%Y-%m-%d'))

        # set to unpublished - should not be included
        pages = Page.objects.exclude(slug='/')  # check all but home page
        pages.update(status=CONTENT_STATUS_DRAFT)
        response = self.client.get(reverse('sitemap'))
        for page in pages.all():
            self.assertNotContains(response, page.get_absolute_url())


@pytest.mark.django_db
def test_absolutize_url():
    https_url = 'https://example.com/some/path/'
    # https url is returned unchanged
    assert absolutize_url(https_url) == https_url
    # testing with default site domain
    current_site = Site.objects.get_current()

    # test site domain without https
    current_site.domain = 'example.org'
    current_site.save()
    local_path = '/foo/bar/'
    assert absolutize_url(local_path) == 'https://example.org/foo/bar/'
    # trailing slash in domain doesn't result in double slash
    current_site.domain = 'example.org/'
    current_site.save()
    assert absolutize_url(local_path) == 'https://example.org/foo/bar/'
    # site at subdomain should work too
    current_site.domain = 'example.org/sub/'
    current_site.save()
    assert absolutize_url(local_path) == 'https://example.org/sub/foo/bar/'
    # site with https:// included
    current_site.domain = 'https://example.org'
    assert absolutize_url(local_path) == 'https://example.org/sub/foo/bar/'



class TestPageSitemap(TestCase):
    fixtures = ['test_pages.json']

    def test_items(self):
        # all fixture items should be included (published, in menus)
        sitemap_items = PageSitemap().items()
        for page in Page.objects.all():
            assert page in sitemap_items

        # set to not in sitemap - should not be included
        pages = Page.objects.exclude(slug='/')  # check all but home page
        pages.update(in_sitemap=False)
        sitemap_items = PageSitemap().items()
        for page in pages.all():
            assert page not in sitemap_items

    def test_priority(self):
        # generic page = default priority
        page = Page.objects.first()
        assert PageSitemap().priority(page) is None

        # landing page = slightly higher
        landingpage = LandingPage.objects.create()
        assert PageSitemap().priority(landingpage.page_ptr) == 0.6

