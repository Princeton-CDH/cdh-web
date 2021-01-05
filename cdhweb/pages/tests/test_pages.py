from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (nested_form_data, rich_text,
                                           streamfield)

from cdhweb.pages.models import ContentPage, HomePage, LandingPage


class TestHomePage(WagtailPageTests):

    def test_can_create(self):
        root = Page.objects.get(title='Root')
        self.assertCanCreate(root, HomePage, nested_form_data({
            'title': 'Home 2',
            'slug': 'home-2',
            'body': streamfield([
                ('paragraph', rich_text('homepage body text')),
            ]),
        }))

    def test_parent_pages(self):
        # only allowed parent is basic page (root)
        self.assertAllowedParentPageTypes(HomePage, [Page])

    def test_subpages(self):
        # landing pages or content pages can be children
        self.assertAllowedSubpageTypes(HomePage, [LandingPage, ContentPage])


class TestLandingPage(WagtailPageTests):
    fixtures = ['test_pages']

    def test_can_create(self):
        home = HomePage.objects.get(title='Home')
        self.assertCanCreate(home, LandingPage, nested_form_data({
            'title': 'Engage',
            'slug': 'engage',
            'tagline': 'Consult, collaborate, and work with us',
            'body': streamfield([
                ('paragraph', rich_text('engage page text')),
            ]),
        }))

    def test_parent_pages(self):
        # only allowed parent is home
        self.assertAllowedParentPageTypes(LandingPage, [HomePage])

    def test_subpages(self):
        # only allowed child is content page
        self.assertAllowedSubpageTypes(LandingPage, [ContentPage])


class TestContentPage(WagtailPageTests):
    fixtures = ['test_pages']

    def test_can_create(self):
        research = LandingPage.objects.get(title='Research')
        self.assertCanCreate(research, ContentPage, nested_form_data({
            'title': 'Data Curation',
            'slug': 'data-curation',
            'body': streamfield([
                ('paragraph', rich_text('data curation page text')),
            ]),
        }))

    def test_parent_pages(self):
        # can be child of home, landing page, or another content page
        self.assertAllowedParentPageTypes(ContentPage,
                                          [HomePage, LandingPage, ContentPage])

    def test_subpages(self):
        # only allowed child is content page
        self.assertAllowedSubpageTypes(ContentPage, [ContentPage])
