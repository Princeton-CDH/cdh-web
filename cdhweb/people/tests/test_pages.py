from cdhweb.people.models import PeopleLandingPage, ProfilePage, Person
from cdhweb.pages.models import ContentPage, HomePage
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (nested_form_data, rich_text,
                                           streamfield)


class TestPeopleLandingPage(WagtailPageTests):

    def setUp(self):
        """create page tree for testing"""
        root = Page.objects.get(title="Root")
        self.home = HomePage()
        root.add_child(self.home)
        root.save()

    def test_can_create(self):
        """should be creatable as child of homepage"""
        self.assertCanCreate(self.home, PeopleLandingPage, nested_form_data({
            "title": "people",
            "body": streamfield([("paragraph", rich_text("body text"))])
        }))

    def test_parent_pages(self):
        """only allowed parent is homepage"""
        self.assertAllowedParentPageTypes(PeopleLandingPage, [HomePage])

    def test_child_pages(self):
        """content pages and profile pages can be children"""
        self.assertAllowedSubpageTypes(
            PeopleLandingPage, [ContentPage, ProfilePage])


class TestProfilePage(WagtailPageTests):

    def setUp(self):
        """create page tree and person for testing"""
        root = Page.objects.get(title="Root")
        home = HomePage()
        root.add_child(home)
        root.save()
        self.lp = PeopleLandingPage()
        home.add_child(self.lp)
        home.save()
        self.person = Person.objects.create(
            first_name="tom", last_name="jones")

    def test_can_create(self):
        """should be creatable as child of people landing page"""
        self.assertCanCreate(self.lp, ProfilePage, nested_form_data({
            "title": "tom r. jones",
            "person": self.person,
            "education": rich_text("school"),
            "bio": streamfield([("paragraph", rich_text("about me"))])
        }))

    def test_parent_pages(self):
        """only allowed parent is people landing page"""
        self.assertAllowedParentPageTypes(ProfilePage, [PeopleLandingPage])

    def test_child_pages(self):
        """no allowed children"""
        self.assertAllowedSubpageTypes(ProfilePage, [])

    def test_delete_handler(self):
        """deleting person should delete corresponding profile"""
        self.lp.add_child(ProfilePage(
            title="tom r. jones",
            person=self.person,
        ))
        self.lp.save()
        self.person.delete()
        assert ProfilePage.objects.count() == 0
