import json
from datetime import date, timedelta, timezone
from unittest import skip

from cdhweb.events.models import Event, EventType
from cdhweb.pages.models import HomePage
from cdhweb.people.models import (AffiliateListPage, ExecListPage, PeopleLandingPage, Person,
                                  PersonListPage, Position, ProfilePage,
                                  SpeakerListPage, StaffListPage,
                                  StudentListPage, Title)
from cdhweb.projects.models import Grant, Membership, Project, Role
from cdhweb.resources.models import PersonResource, ResourceType
from django.contrib.auth import get_user_model
from django.test import TestCase
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)
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
                                start_date=date(2021, 1, 1))
        Position.objects.create(person=self.person, title=director,
                                start_date=date(2020, 1, 1),
                                end_date=date(2020, 10, 1))

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
        self.lp = PeopleLandingPage(title="people", slug="people",
                                    tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # create one current and one past person for testing
        director = Title.objects.create(title="director", sort_order=0)
        tom = Person.objects.create(first_name="tom")
        sam = Person.objects.create(first_name="sam")
        Position.objects.create(person=tom, title=director,
                                start_date=date.today())
        Position.objects.create(person=sam, title=director,
                                start_date=date.today() - timedelta(weeks=20),
                                end_date=date.today() - timedelta(weeks=10),)

        # create a person list page for testing
        self.list_page = PersonListPage(title="my people", slug="my")
        self.lp.add_child(instance=self.list_page)
        self.lp.save()

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
        other_people = PersonListPage(title="other people", slug="other")
        some_people = PersonListPage(title="some people", slug="some")
        for page in [other_people, some_people]:
            self.lp.add_child(instance=page)
            self.lp.save()

        # check that the nav includes other list pages and their URLs
        response = self.client.get(self.list_page.get_url())
        self.assertContains(response,
                            '<li><a href="%s">other people</a></li>' % other_people.get_url(),
                            html=True)
        self.assertContains(response,
                            '<li><a href="%s">some people</a></li>' % some_people.get_url(),
                            html=True)

        # current page should be marked current
        self.assertContains(response,
                            '<li class="current"><a href="%s">my people</a></li>' % self.list_page.get_url(),
                            html=True)


class TestStaffListPage(TestCase):

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
        self.lp = PeopleLandingPage(title="people", slug="people",
                                    tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # create a staff list page for testing
        self.list_page = StaffListPage(title="staff", slug="staff")
        self.lp.add_child(instance=self.list_page)
        self.lp.save()

    @skip("fixme")
    def test_staff_list(self):
        # fixture includes staff person with two positions
        staffer = Person.objects.get(username='staff')
        # postdoc should be listed on staff page
        postdoc = Person.objects.get(username='postdoc')

        response = self.client.get(self.list_page.get_url())
        # person should only appear once even if they have multiple positions
        assert response.context['current'].filter(
            user__username='staff').count() == 1

        # staffer profile should be included
        assert staffer.profile in response.context['current']
        # postdoc profile should also
        assert postdoc.profile in response.context['current']

        cur_post = staffer.positions.first()
        prev_post = staffer.positions.all()[1]
        self.assertContains(response, staffer.profile.title)
        self.assertContains(response, staffer.profile.current_title)
        self.assertContains(response, staffer.profile.get_absolute_url())
        self.assertNotContains(response, prev_post.years)
        self.assertNotContains(response, cur_post.years)

        # postdoc info
        self.assertContains(response, postdoc.profile.title)
        self.assertContains(response, postdoc.profile.current_title)
        self.assertContains(response, postdoc.profile.get_absolute_url())

        # should be listed if position end date is set for future
        cur_post.end_date = date.today() + timedelta(days=1)
        cur_post.save()
        response = self.client.get(self.list_page.get_url())
        assert staffer.profile in response.context['current']

        # should be in past, not current, if position end date has passed
        cur_post.end_date = date.today() - timedelta(days=1)
        cur_post.save()
        response = self.client.get(self.list_page.get_url())
        assert staffer.profile not in response.context['current']
        assert staffer.profile in response.context['past']


class TestStudentListPage(TestCase):

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
        self.lp = PeopleLandingPage(title="people", slug="people",
                                    tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # create a staff list page for testing
        self.list_page = StudentListPage(title="students", slug="students")
        self.lp.add_child(instance=self.list_page)
        self.lp.save()

    @skip("fixme")
    def test_student_list(self):
        # grad, undergrad assistant, PGRA
        grad = Person.objects.get(username='grad')
        undergrad = Person.objects.get(username='undergrad')
        pgra = Person.objects.get(username='pgra')
        # person with student status with a project
        grad_pi = Person.objects.get(username='tom')

        response = self.client.get(self.list_page.get_url())
        assert grad.profile in response.context['current']
        assert pgra.profile in response.context['current']
        assert undergrad.profile in response.context['past']
        assert grad_pi.profile in response.context['past']

        # grad and undergrad have profile pages
        self.assertContains(response, grad.profile.title)
        self.assertContains(response, grad.profile.current_title)
        self.assertContains(response, grad.profile.get_absolute_url())
        self.assertContains(response, undergrad.profile.title)
        # undergrad has no current title, displays first title (with dates)
        self.assertContains(response, undergrad.positions.first().title)
        self.assertContains(response, undergrad.profile.get_absolute_url())
        # grad project director does not have local profile page or title
        self.assertContains(response, grad_pi.profile.title)
        # grad pi does have an external website url
        website = ResourceType.objects.get_or_create(name='Website')[0]
        ext_profile_url = 'http://person.me'
        PersonResource.objects.create(user=grad_pi, resource_type=website,
                                      url=ext_profile_url)
        assert grad_pi.profile_url == ext_profile_url
        response = self.client.get(self.list_page.get_url())
        self.assertContains(response, grad_pi.website_url)


class TestAffiliatesListPage(TestCase):

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
        self.lp = PeopleLandingPage(title="people", slug="people",
                                    tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # create a staff list page for testing
        self.list_page = AffiliateListPage(
            title="affiliates", slug="affiliates")
        self.lp.add_child(instance=self.list_page)
        self.lp.save()

    @skip("fixme")
    def test_affiliates_list(self):
        # faculty person is a project director
        fac = Person.objects.get(username='jk2')
        response = self.client.get(self.list_page.get_url())
        assert fac.profile in response.context['current']

        # should display name and date from latest grant
        grant = fac.latest_grant
        self.assertContains(response, '{}–{} {} Grant Recipient'.format(
            grant.start_date.year,
            grant.end_date.year,
            grant.grant_type.grant_type), html=True)

        # non current membership - should shift to past list
        mship = fac.membership_set.first()
        mship.end_date = date(2018, 1, 1)
        mship.save()
        response = self.client.get(self.list_page.get_url())
        assert fac.profile not in response.context['current']
        assert fac.profile in response.context['past']

        # promote a staff person to faculty director; they should also appear
        staff = Person.objects.get(username='dominick')
        s_co = Project.objects.get(slug='sco')
        s_co_grant = Grant.objects.get(pk=4)
        proj_director = Role.objects.get(title='Project Director')
        Membership.objects.create(
            person=staff, project=s_co, role=proj_director,
            start_date=s_co_grant.start_date, end_date=s_co_grant.end_date)
        response = self.client.get(self.list_page.get_url())
        assert staff.profile in response.context['past']


class TestSpeakersListPage(TestCase):

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
        self.lp = PeopleLandingPage(title="people", slug="people",
                                    tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # create a staff list page for testing
        self.list_page = SpeakerListPage(title="speakers", slug="speakers")
        self.lp.add_child(instance=self.list_page)
        self.lp.save()

    @skip("fixme")
    def test_speakers_list(self):
        # create a test event for an external person
        bill = Person.objects.get(username='billshakes')
        workshop = EventType.objects.get(name='Workshop')
        # use django timezone util for timezone-aware datetime
        start_time = timezone.now() + timedelta(days=1)  # starts tomorrow
        end_time = start_time + timedelta(hours=2)  # lasts 2 hours
        bill_workshop = Event.objects.create(start_time=start_time,
                                             end_time=end_time,
                                             event_type=workshop,
                                             slug='bill-workshop',
                                             status=CONTENT_STATUS_DRAFT)
        bill_workshop.speakers.add(bill)
        # create another event to test ordering
        rms = Person.objects.get(username='rms')
        lecture = EventType.objects.get(name='Guest Lecture')
        start_time = timezone.now() + timedelta(weeks=1)  # starts in a week
        end_time = start_time + timedelta(hours=1)  # lasts 1 hour
        rms_lecture = Event.objects.create(start_time=start_time,
                                           end_time=end_time,
                                           event_type=lecture,
                                           slug='rms-lecture',
                                           status=CONTENT_STATUS_DRAFT)
        rms_lecture.speakers.add(rms)

        response = self.client.get(self.list_page.get_url())
        # no speakers, since no published events exist
        assert len(response.context['current']) == 0

        # publish an event
        bill_workshop.status = CONTENT_STATUS_PUBLISHED
        bill_workshop.save()

        response = self.client.get(self.list_page.get_url())
        # one speaker, since one published event
        assert len(response.context['current']) == 1
        # speaker's profile is listed as upcoming
        assert bill.profile in response.context['current']
        # upcoming event month, day, and time is shown
        self.assertContains(response, bill_workshop.when())
        # event type is shown
        self.assertContains(response, bill_workshop.event_type)
        # speaker institutional affiliation is shown
        self.assertContains(response, bill.profile.institution)
        # link to event is rendered
        self.assertContains(
            response, bill.event_set.first().get_absolute_url())

        # publish another event
        rms_lecture.status = CONTENT_STATUS_PUBLISHED
        rms_lecture.save()

        response = self.client.get(self.list_page.get_url())
        # both speakers should now be listed
        assert len(response.context['current']) == 2

        # speakers should be sorted with earliest event first
        assert response.context['current'][0] == bill.profile
        assert response.context['current'][1] == rms.profile

        # move an event to the past
        new_start = timezone.now() - timedelta(weeks=52)  # ~1 year ago
        bill_workshop.start_time = new_start
        bill_workshop.end_time = new_start + timedelta(hours=2)  # 2 hours long
        bill_workshop.save()

        # should be one profile in each category
        response = self.client.get(self.list_page.get_url())
        assert bill.profile in response.context['past']
        assert rms.profile in response.context['current']

        # year of past event is shown
        self.assertContains(response, bill_workshop.start_time.strftime('%Y'))

        # move both events to past to test ordering
        new_start = timezone.now() - timedelta(weeks=104)  # ~2 years ago
        rms_lecture.start_time = new_start
        rms_lecture.end_time = new_start + timedelta(hours=2)  # 2 hours long
        rms_lecture.save()

        # speakers should be sorted with latest event year first
        response = self.client.get(self.list_page.get_url())
        assert response.context['past'][0] == bill.profile
        assert response.context['past'][1] == rms.profile


class TestExecListView(TestCase):

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
        self.lp = PeopleLandingPage(title="people", slug="people",
                                    tagline="people of the cdh")
        home.add_child(instance=self.lp)
        home.save()

        # create a staff list page for testing
        self.list_page = ExecListPage(title="exec", slug="exec")
        self.lp.add_child(instance=self.list_page)
        self.lp.save()

    @skip("fixme")
    def test_executive_committee_list(self):
        # former acting faculty directory is also exec
        delue = Person.objects.get(username='delue')
        assert delue.profile in Person.objects.executive_committee()

        # sits with committe is also in main exec filter
        jay = Person.objects.get(username='dominick')
        assert jay.profile in Person.objects.executive_committee()

        response = self.client.get(self.list_page.get_url())
        # current committee member - in current
        assert delue.profile in response.context['current']
        # current member, sits with committee - in sits with
        assert jay.profile in response.context['sits_with']
        # alumni currently empty
        assert response.context['past'].count() is 0

        # should show job title, not cdh affiliation
        self.assertContains(response, delue.profile.job_title)
        self.assertContains(response, jay.profile.job_title)
        # should not show delue's cdh position
        self.assertNotContains(response, "Acting Faculty Director")

        # set past end dates on position memberships
        yesterday = date.today() - timedelta(days=1)
        delue.positions.filter(
            end_date__isnull=True).update(end_date=yesterday)
        jay.positions.update(end_date=yesterday)
        response = self.client.get(self.list_page.get_url())
        assert response.context['current'].count() is 0
        assert response.context['sits_with'].count() is 0
        # both committee member and sits with in past
        assert delue.profile in response.context['past']
        assert jay.profile in response.context['past']
        # sits with section not shown when empty
        self.assertNotContains(response, 'Sits with Executive Committee')
