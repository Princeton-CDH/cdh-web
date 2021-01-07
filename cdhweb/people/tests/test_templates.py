import datetime
import json

from cdhweb.pages.models import HomePage
from cdhweb.people.models import (PeopleLandingPage, Person, PersonListPage, Position,
                                  ProfilePage, Title)
from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.core.models import Page, Site


class TestProfilePage(TestCase):

    def setUp(self):
        """create example user/person/profile and testing client"""
        # set up wagtail page tree
        root = Page.objects.get(title="Root")
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        lp = PeopleLandingPage(title="people", slug="people", tagline="people")
        home.add_child(instance=lp)
        home.save()
        site = Site.objects.first()
        site.root_page = home
        site.save()
        self.site = site

        # set up user/person/profile
        User = get_user_model()
        self.user = User.objects.create_user(username="tom")
        self.person = Person.objects.create(user=self.user, first_name="tom")
        self.profile = ProfilePage(
            person=self.person,
            title="tom r. jones",
            slug="tom-jones",
            education="<ul><li>college dropout</li></ul>",
            bio=json.dumps([{"type": "paragraph", "value": "<b>about me</b>"}])
        )
        lp.add_child(instance=self.profile)
        lp.save()

    def test_title(self):
        """profile page should display profile's title"""
        response = self.client.get(self.profile.relative_url(self.site))
        self.assertContains(response, "<h1>tom r. jones</h1>", html=True)

    def test_education(self):
        """profile page should display person's education"""
        response = self.client.get(self.profile.relative_url(self.site))
        self.assertContains(response, "<li>college dropout</li>", html=True)

    def test_bio(self):
        """profile page should display person's bio"""
        response = self.client.get(self.profile.relative_url(self.site))
        self.assertContains(response, "<b>about me</b>", html=True)

    def test_positions(self):
        """profile page should display all positions held by its person"""
        # create some positions
        director = Title.objects.create(title="director")
        developer = Title.objects.create(title="developer")
        Position.objects.create(person=self.person, title=developer,
                                start_date=datetime.date(2021, 1, 1))
        Position.objects.create(person=self.person, title=director,
                                start_date=datetime.date(2020, 1, 1),
                                end_date=datetime.date(2020, 10, 1))

        # should all be displayed with dates
        response = self.client.get(self.profile.relative_url(self.site))
        self.assertContains(response, "<p class='title'>developer</p>",
                            html=True)
        self.assertContains(response, "<p class='title'>2020 director</p>",
                            html=True)


class TestPersonListPage(TestCase):

    def setUp(self):
        """set up wagtail page tree and create testing page"""
        # set up page tree
        site = Site.objects.first()
        root = Page.objects.get(title="Root")
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        site.root_page = home
        site.save()
        lp = PeopleLandingPage(title="people", slug="people",
                               tagline="people of the cdh")
        home.add_child(instance=lp)
        home.save()

        # create one current and one past person for testing
        director = Title.objects.create(title="director", sort_order=0)
        tom = Person.objects.create(first_name="tom")
        sam = Person.objects.create(first_name="sam")
        Position.objects.create(person=tom, title=director,
                                start_date=datetime.date.today())
        Position.objects.create(person=sam, title=director,
                                start_date=datetime.date.today() - datetime.timedelta(weeks=20),
                                end_date=datetime.date.today() - datetime.timedelta(weeks=10),)

        # create a person list page for testing
        self.list_page = PersonListPage(title="My People", slug="my")
        lp.add_child(instance=self.list_page)
        lp.save()

    def test_body(self):
        """person list pages should display editable content"""
        # put some text in the body
        self.list_page.body = json.dumps([
            {"type": "paragraph", "value": "<b>about my people</b>"}
        ])
        self.list_page.save()

        # check it gets rendered
        response = self.client.get(self.list_page.get_url())
        self.assertContains(response, "<b>about my people</b>", html=True)

    def test_headings(self):
        """person list pages should display custom current/past headings"""
        # change the current and past headings
        PersonListPage.current_heading = "new people"
        PersonListPage.past_heading = "old people"

        # check they are rendered
        response = self.client.get(self.list_page.get_url())
        self.assertContains(response, "<h1>new people</h1>", html=True)
        self.assertContains(response, "<h2>old people</h2>", html=True)

    def test_archive_nav(self):
        """person list pages should display a nav menu for other list pages"""
        # create sibling list pages to populate the archive nav
        # check that the nav includes all list pages and their URLs
        response = self.client.get(self.list_page.get_url())
        pass
