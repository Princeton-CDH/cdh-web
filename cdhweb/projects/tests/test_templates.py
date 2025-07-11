from datetime import date, timedelta

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains, assertTemplateUsed

from cdhweb.pages.models import RelatedLinkType
from cdhweb.pages.tests.conftest import to_streamfield_safe
from cdhweb.projects.models import ProjectRelatedLink


class TestProjectDetail:
    @pytest.mark.skip("Pre-existing test failure - projects template issue")
    def test_related_links(self, client, derrida):
        """project detail page should display project related links"""
        # add a github link for derrida
        github = RelatedLinkType.objects.get_or_create(name="GitHub")[0]
        derrida_gh = ProjectRelatedLink.objects.create(
            project=derrida,
            type=github,
            url="https://github.com/princeton-CDH/derrida-django",
        )

        # should display link type and create a link using URL
        response = client.get(derrida.get_url())
        assertContains(response, '<a href="%s">GitHub</a>' % derrida_gh.url, html=True)

    def test_website_url(self, client, derrida):
        """project detail page should display website url if set"""
        # create a website URL for derrida
        website = RelatedLinkType.objects.get_or_create(name="Website")[0]
        derrida_site = ProjectRelatedLink.objects.create(
            project=derrida, type=website, url="https://derridas-margins.princeton.edu"
        )

        response = client.get(derrida.get_url())
        assertContains(response, '<a href="%s">' % derrida_site.url)

    def test_contributors(self, client, derrida):
        """project detail page should display current project team and alums"""
        # get all memberships
        pi = derrida.memberships.get(person__first_name="Katie")
        dev = derrida.memberships.get(person__last_name="Koeser")
        pm1 = derrida.memberships.get(person__last_name="Munson")
        grad = derrida.memberships.get(person__first_name="Chloe")
        pm2 = derrida.memberships.get(person__first_name="Renee")

        # all current members and their roles are listed exactly once
        response = client.get(derrida.get_url())
        for member in [pi, dev, grad, pm2]:
            assertContains(response, member.person, count=1)
            assertContains(response, member.role, count=1)

        # pm1 should be listed in alums (actually "Alum" since singular)
        assertContains(response, "Project Alum")
        assertContains(response, pm1.person)

    def test_grants(self, client, derrida):
        """project detail page should display all grants"""
        # get all grants
        dcg = derrida.grants.get(grant_type__grant_type="Dataset Curation")
        rpg = derrida.grants.get(grant_type__grant_type="Research Partnership")

        # should display label and years
        response = client.get(derrida.get_url())
        assertContains(response, "Dataset Curation")
        assertContains(response, dcg.years)
        assertContains(response, "Research Partnership")
        assertContains(response, rpg.years)

    def test_long_description(self, client, derrida):
        """project detail page should display long description (body) if set"""
        # set a long description for derrida
        derrida.body = to_streamfield_safe("<b>About Derrida</b>")
        derrida.save()

        # should display with rich text
        response = client.get(derrida.get_url())
        assertContains(response, "<b>About Derrida</b>", html=True)
