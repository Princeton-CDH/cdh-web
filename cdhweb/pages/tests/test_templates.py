import pytest
from django.test import TestCase, SimpleTestCase
from wagtail.core.models import Page, Site

from cdhweb.pages.models import HomePage, LandingPage, ContentPage, CaptionedImageBlock, SVGImageBlock


class TestHomePage(TestCase):
    """Test the home page."""
    fixtures = ["test_pages.json"]

    def setUp(self):
        """get objects for use in tests"""
        self.homepage = HomePage.objects.get()
        self.site = Site.objects.get()

    def test_visit(self):
        """homepage should be navigable"""
        response = self.client.get(self.homepage.relative_url(self.site))
        assert response.status_code == 200

    def test_page_content(self):
        """homepage editable content should display"""
        response = self.client.get(self.homepage.relative_url(self.site))
        self.assertContains(response, self.homepage.body[0].value.source)

    def test_blog_posts(self):
        """homepage should display featured blog posts in carousel"""
        # TODO actually check that featured posts appear once blog is exodized
        response = self.client.get(self.homepage.relative_url(self.site))
        self.assertTemplateNotUsed(response, "snippets/carousel.html")

        """
        # add some posts but don't feature any yet; should display most recent 3
        for n in range(1, 8):
            BlogPost.objects.create(title='Post %s' % n)
        response = self.client.get(index_url)
        assert len(response.context['updates']) == 3
        self.assertTemplateUsed(response, 'snippets/carousel.html')
        self.assertContains(response, '<div id="carousel')
        # one "active" slide, the rest are normal
        self.assertContains(
            response, '<div class="post-update active">', count=1)
        self.assertContains(response, '<div class="post-update">', count=2)
        # feature all of the posts; should display most recent 6
        for post in BlogPost.objects.all():
            post.is_featured = True
            post.save()
        response = self.client.get(index_url)
        assert len(response.context['updates']) == 6
        self.assertTemplateUsed(response, 'snippets/carousel.html')
        self.assertContains(response, '<div id="carousel')
        self.assertContains(
            response, '<div class="post-update active">', count=1)
        self.assertContains(response, '<div class="post-update">', count=5)

        # ensure all displayed posts have a title and link
        for post in BlogPost.objects.all()[:6]:
            self.assertContains(response, post.get_absolute_url())
            self.assertContains(response, post.title)
        """

    def test_highlighted_projects(self):
        """homepage should display highlighted projects as cards"""
        # TODO actually check that projects appear once projects are exodized
        response = self.client.get(self.homepage.relative_url(self.site))
        self.assertTemplateNotUsed(
            response, "projects/snippets/project_card.html")

        """
                # test how projects are displayed on the home page
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
        """

    def test_upcoming_events(self):
        """homepage should display upcoming events as cards"""
        # TODO actually check that events appear once events are exodized
        response = self.client.get(self.homepage.relative_url(self.site))
        self.assertTemplateNotUsed(response, "events/snippets/event_card.html")
        self.assertContains(
            response, "Next semester's events are being scheduled.")

        """
        self.assertContains(response, reverse('event:upcoming'),
                            msg_prefix='should link to upcoming events (in lieue of an archive)')

        # test how events are displayed on the home page
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

        # TODO: not yet testing speakers displayed

        # not yet testing published/unpublished
        """


class TestLandingPage(TestCase):
    """Test landing pages."""
    fixtures = ["test_pages.json"]

    def setUp(self):
        """get objects for use in tests"""
        self.landingpage = LandingPage.objects.get(slug="research")
        self.site = Site.objects.get()

    def test_visit(self):
        """landingpage should be navigable"""
        response = self.client.get(self.landingpage.relative_url(self.site))
        assert response.status_code == 200

    def test_page_content(self):
        """landingpage editable content should display"""
        response = self.client.get(self.landingpage.relative_url(self.site))
        self.assertContains(response, self.landingpage.body[0].value.source)

    def test_tagline(self):
        """landingpage tagline should display"""
        response = self.client.get(self.landingpage.relative_url(self.site))
        self.assertContains(response, "Collaborate with us!")

    @pytest.mark.skip("todo")
    def test_header_image(self):
        pass


class TestContentPage(TestCase):
    """Test contentpages."""
    fixtures = ["test_pages.json"]

    def setUp(self):
        """get contentpage objects for use in tests"""
        self.contentpage = ContentPage.objects.get(slug="about")
        self.site = Site.objects.get()

    def test_visit(self):
        """contentpage should be navigable"""
        response = self.client.get(self.contentpage.relative_url(self.site))
        assert response.status_code == 200

    def test_page_content(self):
        """contentpage editable content should display"""
        response = self.client.get(self.contentpage.relative_url(self.site))
        self.assertContains(response, self.contentpage.body[0].value.source)


class TestPagesSitemap(TestCase):

    @pytest.mark.skip("todo")
    def test_sitemap(self):
        # basic test of sitemap url config, override from mezzanine
        pass
        # response = self.client.get(reverse('sitemap'))
        # assert response.status_code == 200

        # # both fixture items are published
        # for page in Page.objects.all():
        #     self.assertContains(response, page.get_absolute_url())
        #     self.assertContains(response, page.updated.strftime('%Y-%m-%d'))

        # # set to unpublished - should not be included
        # pages = Page.objects.exclude(slug='/')  # check all but home page
        # # pages.update(status=CONTENT_STATUS_DRAFT)
        # # response = self.client.get(reverse('sitemap'))
        # for page in pages.all():
        #     self.assertNotContains(response, page.get_absolute_url())


class TestPagesMenus(TestCase):

    @pytest.mark.skip("todo")
    def test_child_pages_attachment(self):
        about = Page.objects.get(title='About')
        annual_report = Page.objects.get(title='Annual Report')
        response = self.client.get(about.get_absolute_url())
        # page-children attachment section should be present
        self.assertContains(
            response, '<div class="attachments page-children">')
        # child page title and url should be present
        self.assertContains(response, annual_report.title)
        self.assertContains(response, annual_report.get_absolute_url())

        # delete child page to check behavior without
        annual_report.delete()
        response = self.client.get(about.get_absolute_url())
        # should not error, should not contain page-children attachment section
        self.assertNotContains(
            response, '<div class="attachments page-children">')


class TestCaptionedImageBlock(SimpleTestCase):

    def test_render(self):
        block = CaptionedImageBlock()
        test_img = {'url': 'kitty.png', 'width': 100, 'height': 200}
        alt_text = 'picture of a kitten'
        # NOTE: using "img" here instead of "image" means we're
        # not actually testing the image logic; but not clear how
        # to mock or use an image object in a test
        html = block.render(block.to_python({
            'img': test_img, 'alternative_text': alt_text
        }))
        assert '<figure>' in html
        assert '<img srcset="' in html
        assert 'alt="picture of a kitten" ' in html
        # no caption
        assert '<figcaption>' not in html

        # with caption
        caption = 'A kitten curled up in the sunshine'
        html = block.render(block.to_python({
            'img': test_img, 'alternative_text': alt_text,
            'caption': caption}))
        assert '<figcaption>' in html
        assert caption in html


class TestSVGImageBlock(SimpleTestCase):

    def test_render(self):
        block = SVGImageBlock()
        test_svg = {'url': 'graph.svg'}  # Mock(spec=Document, url='graph.svg')
        alt_text = 'membership timeline'
        html = block.render({
            'image': test_svg, 'alternative_text': alt_text
        })
        assert ('<figure ') in html
        assert '<img role="img" ' in html
        # no caption, no extended description
        assert '<figcaption>' not in html
        assert '<div class="sr-only" ' not in html

        # with caption & extended description
        caption = 'membership activity from 1919 to 1942'
        desc = 'chart shows activity in 1920 and 1940'
        html = block.render({
            'image': test_svg, 'alternative_text': alt_text,
            'caption': caption, 'extended_description': desc})
        assert ('<figcaption>%s</figcaption' % caption) in html
        assert '<div class="sr-only" id="graphsvg-desc">' in html
        assert desc in html
