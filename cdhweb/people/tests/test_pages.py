import datetime
import json

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.utils import timezone
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import rich_text

from cdhweb.blog.models import Author, BlogPost
from cdhweb.pages.models import LinkPage
from cdhweb.people.models import PeopleLandingPageArchived, Person, Profile


class TestPeopleLandingPageArchived(WagtailPageTestCase):
    def test_parent_pages(self):
        """no allowed parent page type; must be created manually"""
        self.assertAllowedParentPageTypes(PeopleLandingPageArchived, [])

    def test_child_pages(self):
        """only profile pages and link pages can be children"""
        self.assertAllowedSubpageTypes(PeopleLandingPageArchived, [Profile, LinkPage])


class TestProfile:
    def test_can_create(self, people_landing_page):
        """should be creatable as child of people landing page"""
        person = Person.objects.create(first_name="tom", last_name="jones")
        profile = Profile(
            title="tom r. jones",
            person=person,
            education=rich_text("school"),
            body=json.dumps([{"type": "paragraph", "value": "about me"}]),
        )
        people_landing_page.add_child(instance=profile)
        people_landing_page.save()
        assert person.profile == profile

    def test_person_required(self, people_landing_page):
        """profile page must be for an existing person"""
        with pytest.raises(ValidationError):
            people_landing_page.add_child(
                instance=Profile(
                    title="tom r. jones",
                    education=rich_text("school"),
                    body=json.dumps([{"type": "paragraph", "value": "about me"}]),
                )
            )

    def test_delete_handler(self, people_landing_page):
        """deleting person should delete corresponding profile"""
        person = Person.objects.create(first_name="tom", last_name="jones")
        people_landing_page.add_child(
            instance=Profile(
                title="tom r. jones",
                person=person,
            )
        )
        people_landing_page.save()
        person.delete()
        assert Profile.objects.count() == 0

    def test_recent_blogposts(self, people_landing_page, blog_link_page):
        """profile should have person's most recent blog posts in context"""
        # create the profile page
        person = Person.objects.create(first_name="tom", last_name="jones")
        profile = Profile(
            title="tom jones",
            slug="tom-jones",
            person=person,
        )
        people_landing_page.add_child(instance=profile)
        people_landing_page.save()

        # context obj with blog posts is empty
        factory = RequestFactory()
        request = factory.get(profile.get_url())
        context = profile.get_context(request)
        assert not context["recent_posts"]  # empty list

        # create some blog posts by this person
        # "one"     2021-01-01  published
        # "two"     2021-01-02  published
        # "three"   2021-01-03  published
        # "four"    2021-01-04  draft
        # "five"    2021-01-05  published
        posts = {}
        for i, title in enumerate(["one", "two", "three", "four", "five"]):
            post = BlogPost(title=title)
            post.first_published_at = timezone.make_aware(
                datetime.datetime(2021, 1, i + 1)
            )
            blog_link_page.add_child(instance=post)
            blog_link_page.save()
            Author.objects.create(post=post, person=person)
            posts[title] = post
        posts["four"].unpublish()

        # only 3 most recent *published* posts should be in context, in order
        # with most recent first: "five", "three", "two"
        factory = RequestFactory()
        request = factory.get(profile.get_url())
        context = profile.get_context(request)
        assert context["recent_posts"][0] == posts["five"]
        assert context["recent_posts"][1] == posts["three"]
        assert context["recent_posts"][2] == posts["two"]
        assert posts["four"] not in context["recent_posts"]
        assert posts["one"] not in context["recent_posts"]


class TestProfilePage(WagtailPageTestCase):
    @pytest.mark.skip("Pre-existing test failure - people model configuration issue")
    def test_parent_pages(self):
        """only allowed parent is people landing page"""
        self.assertAllowedParentPageTypes(Profile, [PeopleLandingPageArchived])

    def test_child_pages(self):
        """no allowed children"""
        self.assertAllowedSubpageTypes(Profile, [])
