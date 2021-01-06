import datetime
import json

from cdhweb.pages.models import HomePage
from cdhweb.people.models import (PeopleLandingPage, Person, Position,
                                  ProfilePage, Title)
from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.core.models import Page, Site
from wagtail.tests.utils.form_data import rich_text


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
