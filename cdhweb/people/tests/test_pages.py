import json

import pytest
from cdhweb.pages.models import HomePage
from cdhweb.people.models import PeopleLandingPage, Person, ProfilePage
from django.core.exceptions import ValidationError
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (nested_form_data, rich_text,
                                           streamfield)


class TestPeopleLandingPage(WagtailPageTests):

    def setUp(self):
        """create page tree for testing"""
        root = Page.objects.get(title="Root")
        self.home = HomePage(title="home", slug="")
        root.add_child(instance=self.home)
        root.save()

    def test_parent_pages(self):
        """no allowed parent page type; must be created manually"""
        self.assertAllowedParentPageTypes(PeopleLandingPage, [])

    def test_child_pages(self):
        """only profile pages can be children"""
        self.assertAllowedSubpageTypes(
            PeopleLandingPage, [ProfilePage])


class TestProfilePage(WagtailPageTests):

    def setUp(self):
        """create page tree and person for testing"""
        root = Page.objects.get(title="Root")
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        self.lp = PeopleLandingPage(
            title="people", slug="people", tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()
        self.person = Person.objects.create(
            first_name="tom", last_name="jones")

    def test_parent_pages(self):
        """only allowed parent is people landing page"""
        self.assertAllowedParentPageTypes(ProfilePage, [PeopleLandingPage])

    def test_child_pages(self):
        """no allowed children"""
        self.assertAllowedSubpageTypes(ProfilePage, [])

    def test_can_create(self):
        """should be creatable as child of people landing page"""
        profile = ProfilePage(
            title="tom r. jones",
            person=self.person,
            education=rich_text("school"),
            bio=json.dumps([{"type": "paragraph", "value": "about me"}])
        )
        self.lp.add_child(instance=profile)
        self.lp.save()
        assert self.person.profilepage == profile

    def test_person_required(self):
        """profile page must be for an existing person"""
        with pytest.raises(ValidationError):
            self.lp.add_child(instance=ProfilePage(
                title="tom r. jones",
                education=rich_text("school"),
                bio=json.dumps([{"type": "paragraph", "value": "about me"}])
            ))

    def test_delete_handler(self):
        """deleting person should delete corresponding profile"""
        self.lp.add_child(instance=ProfilePage(
            title="tom r. jones",
            person=self.person,
        ))
        self.lp.save()
        self.person.delete()
        assert ProfilePage.objects.count() == 0
