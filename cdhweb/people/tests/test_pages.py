import json
from datetime import date, datetime, timedelta, timezone

import pytest
from cdhweb.blog.models import BlogPost
from cdhweb.pages.models import HomePage
from cdhweb.people.models import (PeopleLandingPage, Person, PersonListPage,
                                  Position, ProfilePage, StaffListPage, Title)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)
from wagtail.core.models import Page, Site
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import rich_text


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
        site = Site.objects.first()
        root = Page.objects.get(title="Root")
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        site.root_page = home
        site.save()
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

    def test_recent_blogposts(self):
        """profile should have person's most recent blog posts in context"""
        # FIXME create a user since BlogPost still currently assoc. with User
        User = get_user_model()
        tom = User.objects.create_user(username="tom")
        self.person.user = tom

        # create the profile page
        profile = ProfilePage(
            title="tom jones",
            slug="tom-jones",
            person=self.person,
        )
        self.lp.add_child(instance=profile)
        self.lp.save()

        # context obj with blog posts is empty
        factory = RequestFactory()
        request = factory.get(profile.get_url())
        context = profile.get_context(request)
        assert len(context["recent_posts"]) == 0

        # create some blog posts by this person
        # "one"     2021-01-01  published
        # "two"     2021-01-02  published
        # "three"   2021-01-03  published
        # "four"    2021-01-04  draft
        # "five"    2021-01-05  published
        posts = {}
        for i, title in enumerate(["one", "two", "three", "four", "five"]):
            post = BlogPost(title=title)
            post.publish_date = datetime(2021, 1, i + 1,
                                         tzinfo=timezone.utc)
            if title == "four":
                post.status = CONTENT_STATUS_DRAFT
            else:
                post.status = CONTENT_STATUS_PUBLISHED
            post.save()
            post.users.add(tom)
            posts[title] = post

        # only 3 most recent published posts should be in context
        # "five", "three", "two"
        factory = RequestFactory()
        request = factory.get(profile.get_url())
        context = profile.get_context(request)
        assert posts["five"] in context["recent_posts"]
        assert posts["three"] in context["recent_posts"]
        assert posts["two"] in context["recent_posts"]
        assert posts["four"] not in context["recent_posts"]
        assert posts["one"] not in context["recent_posts"]


class TestPersonListPage(WagtailPageTests):

    def setUp(self):
        """fix wagtail page tree and create people for testing"""
        # set up page tree
        site = Site.objects.first()
        root = Page.objects.get(title="Root")
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        site.root_page = home
        site.save()
        self.lp = PeopleLandingPage(
            title="people", slug="people", tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # set up testing people and positions
        director = Title.objects.create(title="director", sort_order=0)
        dev = Title.objects.create(title="developer", sort_order=1)
        self.tom = Person.objects.create(first_name="tom", last_name="a")
        self.sam = Person.objects.create(first_name="sam", last_name="b")
        self.jim = Person.objects.create(first_name="jim", last_name="c")
        self.ben = Person.objects.create(first_name="ben", last_name="d")
        Position.objects.create(person=self.tom, title=director,
                                start_date=date.today())
        Position.objects.create(person=self.sam, title=dev,
                                start_date=date.today())
        Position.objects.create(person=self.jim, title=director,
                                start_date=date.today() - timedelta(weeks=20),
                                end_date=date.today() - timedelta(weeks=10),)
        Position.objects.create(person=self.ben, title=dev,
                                start_date=date.today() - timedelta(weeks=20),
                                end_date=date.today() - timedelta(weeks=10),)

    def test_parent_pages(self):
        """only allowed parent is people landing page"""
        self.assertAllowedParentPageTypes(PersonListPage, [])

    def test_child_pages(self):
        """no allowed children"""
        self.assertAllowedSubpageTypes(PersonListPage, [])

    def test_archive_nav_urls(self):
        """should aggregate a list of other person list pages and their urls"""
        # create several list pages
        list_pages = {}
        for title in ["Staff", "Students", "Affiliates"]:
            list_page = PersonListPage(title=title, slug=title)
            self.lp.add_child(instance=list_page)
            self.lp.save()
            list_pages[title] = list_page

        # pick any one of them; should have a list of its siblings + their urls
        nav_urls = list_pages["Staff"].archive_nav_urls()
        assert (("Staff", list_pages["Staff"].get_url()) in nav_urls)
        assert (("Students", list_pages["Students"].get_url()) in nav_urls)
        assert (("Affiliates", list_pages["Affiliates"].get_url()) in nav_urls)

    def test_get_people(self):
        """should get all people ordered by position"""
        # create a list page
        list_page = PersonListPage(title="People", slug="mine")
        self.lp.add_child(instance=list_page)
        self.lp.save()

        # default order is by last name
        people = list_page.get_people()
        assert people[0] == self.tom    # a, tom
        assert people[1] == self.sam    # b, sam
        assert people[2] == self.jim    # c, jim
        assert people[3] == self.ben    # d, ben

    def test_get_current_people(self):
        """should get current people ordered by position"""
        # create a list page
        list_page = PersonListPage(title="People", slug="mine")
        self.lp.add_child(instance=list_page)
        self.lp.save()

        # current people ordered by last name
        assert list_page.get_current_people()[0] == self.tom
        assert list_page.get_current_people()[1] == self.sam

        # past people are not included
        assert self.jim not in list_page.get_current_people()
        assert self.ben not in list_page.get_current_people()

    def test_get_past_people(self):
        """should get past people ordered by position"""
        # create a list page
        list_page = PersonListPage(title="People", slug="mine")
        self.lp.add_child(instance=list_page)
        self.lp.save()

        # past people ordered by last name
        assert list_page.get_past_people()[0] == self.jim
        assert list_page.get_past_people()[1] == self.ben

        # current people are not included
        assert self.tom not in list_page.get_past_people()
        assert self.sam not in list_page.get_past_people()


class TestStaffListPage(WagtailPageTests):

    def setUp(self):
        """fix wagtail page tree and create people for testing"""
        # set up page tree
        site = Site.objects.first()
        root = Page.objects.get(title="Root")
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        site.root_page = home
        site.save()
        lp = PeopleLandingPage(
            title="people", slug="people", tagline="people of the cdh")
        home.add_child(instance=lp)
        home.save()

        # set up testing people and positions
        # FIXME why is this necessary?
        Title.objects.all().delete()
        exec = Title.objects.create(title="Executive Committee Member", sort_order=2)
        director = Title.objects.create(title="director", sort_order=0)
        dev = Title.objects.create(title="developer", sort_order=1)
        self.tom = Person.objects.create(
            first_name="tom", last_name="x", cdh_staff=True)
        self.sam = Person.objects.create(
            first_name="sam", last_name="n", cdh_staff=True)
        self.jim = Person.objects.create(
            first_name="jim", last_name="l", cdh_staff=True)
        self.ben = Person.objects.create(
            first_name="ben", last_name="a", cdh_staff=True)
        self.bev = Person.objects.create(first_name="bev", last_name="c")
        self.ada = Person.objects.create(first_name="ada", last_name="p",
            cdh_staff=True)
        Position.objects.create(person=self.tom, title=director,
                                start_date=date.today())
        Position.objects.create(person=self.sam, title=dev,
                                start_date=date.today())
        Position.objects.create(person=self.ada, title=exec,
                                start_date=date.today())
        Position.objects.create(person=self.jim, title=director,
                                start_date=date.today() - timedelta(weeks=20),
                                end_date=date.today() - timedelta(weeks=10),)
        Position.objects.create(person=self.ben, title=dev,
                                start_date=date.today() - timedelta(weeks=20),
                                end_date=date.today() - timedelta(weeks=10),)

        # create a staff list page for testing
        self.list_page = StaffListPage(title="CDH Staff", slug="staff")
        lp.add_child(instance=self.list_page)
        lp.save()
        self.factory = RequestFactory()

    def test_current_people(self):
        """should get current cdh staff ordered by position"""
        request = self.factory.get(self.list_page.get_url())
        people = self.list_page.get_context(request)["current_people"]

        # current staff with director first
        assert people[0] == self.tom
        assert people[1] == self.sam

        # past staff not listed
        assert self.jim not in people
        assert self.ben not in people

        # exec not listed
        assert self.ada not in people

        # non-staff not listed
        assert self.bev not in people

    def test_past_people(self):
        """should get past cdh staff ordered by position"""
        request = self.factory.get(self.list_page.get_url())
        people = self.list_page.get_context(request)["past_people"]

        # past staff with director first
        assert people[0] == self.jim
        assert people[1] == self.ben

        # current staff not listed
        assert self.tom not in people
        assert self.sam not in people

        # exec not listed
        assert self.ada not in people

        # non-staff not listed
        assert self.bev not in people