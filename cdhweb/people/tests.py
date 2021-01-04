from datetime import date, timedelta
from unittest.mock import Mock

import pytest
from cdhweb.events.models import Event, EventType
from cdhweb.people.models import (Person, Position, Profile, Title,
                                  init_person_from_ldap)
from cdhweb.people.sitemaps import ProfileSitemap
from cdhweb.projects.models import Grant, Membership, Project, Role
from cdhweb.resources.models import ResourceType, PersonResource
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)


@pytest.mark.django_db
class TestTitle(TestCase):
    fixtures = ['test_people_data.json']

    def test_num_people(self):
        # test counts against fixture data
        faculty_director = Title.objects.filter(
            title='Faculty Director').first()
        assert faculty_director.num_people() == 1
        lead_developer = Title.objects.filter(title='Lead Developer').first()
        assert lead_developer.num_people() == 1


@pytest.mark.django_db
class TestPerson(TestCase):
    fixtures = ['test_people_data.json']

    def test_current_title(self):
        # create test person and add two positions
        staffer = Person.objects.get(username='staff')
        newest_position = staffer.positions.first()
        assert staffer.current_title == newest_position.title

    def test_str(self):
        # username is used if that's all that's available only
        pers = Person(username='foo')
        assert str(pers) == pers.username
        # one name only - no trailing whitespace
        pers.first_name = 'Guinevere'
        assert str(pers) == pers.first_name
        # last and first name both present
        pers.last_name = 'DuLac'
        assert str(pers) == '%s %s' % (pers.first_name, pers.last_name)
        # profile title takes precedence
        pers.save()

        Profile.objects.create(user=pers, title='Gwen of the Lake')
        assert str(pers) == pers.profile.title

    def test_cdh_staff(self):
        pers = Person.objects.create(username='foo')
        assert not pers.cdh_staff()
        profile = Profile.objects.create(user=pers, is_staff=False)
        assert not pers.cdh_staff()

        profile.is_staff = True
        profile.save()
        assert pers.cdh_staff()

    def test_get_absolute_url(self):
        pers = Person.objects.create(username='foo')
        assert pers.get_absolute_url() is None
        profile = Profile.objects.create(user=pers, slug='foo-bar')
        assert pers.get_absolute_url() == profile.get_absolute_url()

    def test_website_url(self):
        pers = Person.objects.create(username='foo')
        assert pers.website_url is None

        # add a website url
        website = ResourceType.objects.get_or_create(name='Website')[0]
        ext_profile_url = 'http://person.me'
        PersonResource.objects.create(user=pers, resource_type=website,
                                    url=ext_profile_url)
        assert pers.website_url == ext_profile_url

    def test_profile_url(self):
        pers = Person.objects.create(username='pers')
        # no urls
        assert pers.profile_url is None

        # username tom in fixture has a website url resource
        grad_pi = Person.objects.get(username='tom')
        ext_profile_url = grad_pi.userresource_set.first().url
        assert grad_pi.profile_url == ext_profile_url

        # local profile takes precedence over external if is_staff is set
        grad_pi.profile.is_staff = True
        grad_pi.profile.status = CONTENT_STATUS_PUBLISHED
        grad_pi.profile.save()
        assert grad_pi.profile_url == grad_pi.profile.get_absolute_url()

        # non-staff profile, should fall back to external
        grad_pi.profile.is_staff = False
        grad_pi.profile.save()
        assert grad_pi.profile_url == ext_profile_url


class TestProfile(TestCase):

    def test_str(self):
        pers = Person(username='foo', first_name='Jean', last_name='Smith')
        profile = Profile(user=pers)
        assert str(profile) == '%s %s' % (pers.first_name, pers.last_name)

    def test_get_absolute_url(self):
        pers = Person(username='foo', first_name='Jean', last_name='Jones')
        profile = Profile(user=pers, slug='jean-jones')
        assert profile.get_absolute_url() == \
            reverse('people:profile', kwargs={'slug': profile.slug})

    def test_current_title(self):
        pers = Person.objects.create(
            username='foo', first_name='Jean', last_name='Jones')
        profile = Profile.objects.create(user=pers, slug='jean-jones')
        # no position
        assert profile.current_title is None

        # previous position, no current
        fellow = Title.objects.create(title='fellow')
        postdoc = Title.objects.create(title='post-doc')
        prev_post = Position.objects.create(user=pers, title=postdoc,
                                            start_date='2015-01-01', end_date='2015-12-31')
        assert profile.current_title is None

        # current position
        staff_title = Title.objects.create(title='staff')
        cur_post = Position.objects.create(user=pers, title=staff_title,
                                           start_date=date(2016, 6, 1))
        assert profile.current_title == cur_post.title


@pytest.mark.django_db
class ProfileQuerySetTest(TestCase):
    fixtures = ['test_people_data.json']

    def test_is_staff(self):
        staffer = Person.objects.get(username='staff')
        grad_pi = Person.objects.get(username='tom')
        postdoc = Person.objects.get(username='postdoc')

        staff = Profile.objects.staff()
        assert staffer.profile in staff
        assert postdoc.profile in staff
        assert grad_pi.profile not in staff

    def test_current(self):
        # no position - should not be in current
        staff2 = Person.objects.get(username='staff2')
        assert staff2.profile not in Profile.objects.current()

        # current post - no end date
        staffer = Person.objects.get(username='staff')
        assert staffer.profile in Profile.objects.current()

        # end date in future also considered current
        cur_post = staffer.positions.first()
        cur_post.end_date = date.today() + timedelta(days=30)
        cur_post.save()
        assert staffer.profile in Profile.objects.current()

        # previous position = not current
        cur_post.delete()
        assert staffer.profile not in Profile.objects.current()

        # grad affiliate with past grant project
        grad_pi = Person.objects.get(username='tom')
        assert grad_pi.profile not in Profile.objects.current()
        mship = grad_pi.membership_set.first()
        # no end date = current
        mship.end_date = None
        mship.save()
        assert grad_pi.profile in Profile.objects.current()
        # end date in future = current
        mship.end_date = date.today() + timedelta(days=30)
        mship.save()
        assert grad_pi.profile in Profile.objects.current()
        # end today = still current
        mship.end_date = date.today()
        mship.save()
        assert grad_pi.profile in Profile.objects.current()

        # grad pm on based on membership dates
        grad_pm = Person.objects.get(username='mary')
        assert grad_pm.profile in Profile.objects.current()
        # set end date to past
        pm_membership = grad_pm.membership_set.first()
        pm_membership.end_date = date.today() - timedelta(days=30)
        pm_membership.save()
        # past should make not current even though grant is active
        assert grad_pm.profile not in Profile.objects.current()

    def test_order_by_position(self):
        director = Person.objects.get(username='Meredith')
        staff = Person.objects.get(username='staff')
        profiles = Profile.objects.filter(user__username__in=['Meredith', 'staff']) \
                                  .order_by_position()
        # sort by position title order
        assert director.profile == profiles[0]
        assert staff.profile == profiles[1]

        # second staffer with same title as staffer but later start
        staffer = Person.objects.get(username='staff')
        staffer2 = Person.objects.get(username='staff2')
        Position.objects.create(user=staffer2, title=staffer.current_title,
                                start_date=date(2016, 12, 1))
        profiles = Profile.objects \
            .filter(user__positions__title__title='staff').order_by_position()
        # should sort by start date, earliest first
        assert staffer.profile == profiles[0]
        assert staffer2.profile == profiles[1]

    def test_student_affiliates(self):
        staffer = Person.objects.get(username='staff')
        grad = Person.objects.get(username='grad')
        undergrad = Person.objects.get(username='undergrad')
        grad_pi = Person.objects.get(username='tom')
        grad_pm = Person.objects.get(username='mary')
        pgra = Person.objects.get(username='pgra')

        assert staffer.profile not in Profile.objects.student_affiliates()
        assert grad.profile in Profile.objects.student_affiliates()
        assert undergrad.profile in Profile.objects.student_affiliates()
        assert grad_pi.profile in Profile.objects.student_affiliates()
        assert grad_pm.profile in Profile.objects.student_affiliates()
        assert pgra.profile in Profile.objects.student_affiliates()

        # grad pi & pm affiliation based on project membership
        grad_pi.membership_set.all().delete()
        grad_pm.membership_set.all().delete()
        assert grad_pi.profile not in Profile.objects.student_affiliates()
        assert grad_pm.profile not in Profile.objects.student_affiliates()

    def test_affiliates(self):
        # faculty person who is also project director should be affiliate
        # (josh is already a project director for s&co)
        faculty = Person.objects.get(username='jk2')
        assert faculty.profile in Profile.objects.affiliates()

        # faculty person with co-PI: Research Lead should be affiliate
        co_pi = Person.objects.create(username='copi')
        co_pi_profile = Profile.objects.create(
            user=co_pi, title="Co-PI", pu_status='fac')
        co_pi_role, _created = Role.objects.get_or_create(
            title='Co-PI: Research Lead')
        s_co_grant = Grant.objects.get(pk=4)
        s_co = Project.objects.get(slug='sco')
        Membership.objects.create(
            person=co_pi, project=s_co, role=co_pi_role,
            start_date=s_co_grant.start_date, end_date=s_co_grant.end_date)
        assert co_pi.profile in Profile.objects.affiliates()

        # staff project director is also an affiliate
        # (make jay dominick a project director on s&co)
        staff = Person.objects.get(username='dominick')
        proj_director = Role.objects.get(title='Project Director')
        Membership.objects.create(
            person=staff, project=s_co, role=proj_director,
            start_date=s_co_grant.start_date, end_date=s_co_grant.end_date)
        assert staff.profile in Profile.objects.affiliates()

        # student project director is not an affiliate
        # (promote "tom", grad PI, to project director)
        grad_pi = Person.objects.get(username='tom')
        Membership.objects.create(
            person=grad_pi, project=s_co, role=proj_director,
            start_date=s_co_grant.start_date)
        assert grad_pi.profile not in Profile.objects.affiliates()

        # CDH staff are not affiliates
        # (meredith is already project director for PPA)
        cdh_staff = Person.objects.get(username='Meredith')
        assert cdh_staff.profile not in Profile.objects.affiliates()

    def test_executive_committee(self):
        # faculty director is not exec
        fac = Person.objects.get(username='Meredith')
        assert fac.profile not in Profile.objects.executive_committee()

        # former acting faculty directory is also exec
        delue = Person.objects.get(username='delue')
        assert delue.profile in Profile.objects.executive_committee()

        # sits with committe is also in main exec filter
        jay = Person.objects.get(username='dominick')
        assert jay.profile in Profile.objects.executive_committee()

    def test_exec_member(self):
        # exec committee member
        delue = Person.objects.get(username='delue')
        assert delue.profile in Profile.objects.exec_member()

        # sits with committe is not exec member
        jay = Person.objects.get(username='dominick')
        assert jay.profile not in Profile.objects.exec_member()

    def test_sits_with_exec(self):
        # exec committee member
        delue = Person.objects.get(username='delue')
        assert delue.profile not in Profile.objects.sits_with_exec()

        # sits with committe
        jay = Person.objects.get(username='dominick')
        assert jay.profile in Profile.objects.sits_with_exec()

    def test_grant_years(self):
        # no error for non-grantees
        Profile.objects.filter(
            user__membership__isnull=True).grant_years().order_by('-user__last_name')

        annotated = Profile.objects.filter(user__membership__role__title='Project Director') \
                                   .grant_years().order_by('-user__last_name')
        for profile in annotated:
            memberships = profile.user.membership_set.order_by('start_date')
            assert profile.first_start == memberships.first().start_date
            assert isinstance(profile.first_start, date)
            assert profile.last_end == memberships.last().end_date
            assert isinstance(profile.last_end, date)


class TestPosition(TestCase):

    def test_str(self):
        staff_title = Title.objects.create(title='staff', sort_order=2)
        director = Person.objects.create(username='director')
        pos = Position.objects.create(user=director, title=staff_title,
                                      start_date=date.today())

        assert str(pos) == '%s %s (%s)' % (director, staff_title,
                                           pos.start_date.year)


@pytest.mark.django_db
def test_init_person_from_ldap():
    # create user to test with
    User = get_user_model()
    staff_user = User.objects.create_user(username='staff',
                                          email='STAFF@EXAMPLE.com')

    # use Mock to simulate ldap data provided by pucas
    ldapinfo = Mock(displayName='Joe E. Schmoe',
                    # no telephone or office set
                    telephoneNumber=[], street=[],
                    title='Freeloader, World at large', pustatus='stf',
                    ou='English')
    init_person_from_ldap(staff_user, ldapinfo)
    staff_person = Person.objects.get(user=staff_user)

    # email should be converted to lower case
    assert staff_user.email == "staff@example.com"

    # person should have been created
    assert staff_user.person == staff_person

    # names should be added correctly
    assert staff_person.first_name == "Joe"
    assert staff_person.last_name == "Schmoe"

    # person fields should be autopopulated where content exists
    assert staff_person.job_title == "Freeloader"
    assert staff_person.phone_number == ""
    assert staff_person.office_location == ""
    assert staff_person.pu_status == "stf"
    assert staff_person.department == "English"

    # add info for telephone number and office location
    ldapinfo.telephoneNumber = "4800"
    ldapinfo.street = "801B"
    init_person_from_ldap(staff_user, ldapinfo)
    staff_person = Person.objects.get(user=staff_user)
    assert staff_person.phone_number == "4800"
    assert staff_person.office_location == "801B"

    # when updating, existing fields should not change
    staff_person.job_title = "New Job"
    staff_person.department = "History"
    staff_person.save()
    init_person_from_ldap(staff_user, ldapinfo)
    staff_person = Person.objects.get(user=staff_user)
    assert staff_person.job_title == "New Job"
    assert staff_person.department == "History"


class TestViews(TestCase):
    fixtures = ['test_people_data']

    def test_staff_redirect(self):
        # valid id gives permanent redirect to slug url
        slug = 'claus-the-chicken'
        response = self.client.get('/about/staff/%s/' % slug)
        assert response.status_code == 301   # moved permanently
        assert response.url == reverse('people:profile', kwargs={'slug': slug})

    def test_staff_list(self):
        # fixture includes staff person with two positions
        staffer = Person.objects.get(username='staff')
        # postdoc should be listed on staff page
        postdoc = Person.objects.get(username='postdoc')

        response = self.client.get(reverse('people:staff'))
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
        response = self.client.get(reverse('people:staff'))
        assert staffer.profile in response.context['current']
        # should be in past, not current, if position end date has passed
        cur_post.end_date = date.today() - timedelta(days=1)
        cur_post.save()
        response = self.client.get(reverse('people:staff'))
        assert staffer.profile not in response.context['current']
        assert staffer.profile in response.context['past']

        # should link to other people pages
        self.assertContains(response, reverse('people:students'))

    def test_student_list(self):
        # grad, undergrad assistant, PGRA
        grad = Person.objects.get(username='grad')
        undergrad = Person.objects.get(username='undergrad')
        pgra = Person.objects.get(username='pgra')
        # person with student status with a project
        grad_pi = Person.objects.get(username='tom')

        response = self.client.get(reverse('people:students'))
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
        response = self.client.get(reverse('people:students'))
        self.assertContains(response, grad_pi.website_url)

    def test_affiliates_list(self):
        # faculty person is a project director
        fac = Person.objects.get(username='jk2')
        response = self.client.get(reverse('people:affiliates'))
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
        response = self.client.get(reverse('people:affiliates'))
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
        response = self.client.get(reverse('people:affiliates'))
        assert staff.profile in response.context['past']

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

        response = self.client.get(reverse('people:speakers'))
        # no speakers, since no published events exist
        assert len(response.context['current']) == 0

        # publish an event
        bill_workshop.status = CONTENT_STATUS_PUBLISHED
        bill_workshop.save()

        response = self.client.get(reverse('people:speakers'))
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

        response = self.client.get(reverse('people:speakers'))
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
        response = self.client.get(reverse('people:speakers'))
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
        response = self.client.get(reverse('people:speakers'))
        assert response.context['past'][0] == bill.profile
        assert response.context['past'][1] == rms.profile

    def test_executive_committee_list(self):
        # former acting faculty directory is also exec
        delue = Person.objects.get(username='delue')
        assert delue.profile in Profile.objects.executive_committee()

        # sits with committe is also in main exec filter
        jay = Person.objects.get(username='dominick')
        assert jay.profile in Profile.objects.executive_committee()

        response = self.client.get(reverse('people:exec-committee'))
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
        response = self.client.get(reverse('people:exec-committee'))
        assert response.context['current'].count() is 0
        assert response.context['sits_with'].count() is 0
        # both committee member and sits with in past
        assert delue.profile in response.context['past']
        assert jay.profile in response.context['past']
        # sits with section not shown when empty
        self.assertNotContains(response, 'Sits with Executive Committee')

    def test_profile_detail(self):
        # create test person and add two positions
        staffer = Person.objects.get(username='staff')

        response = self.client.get(staffer.get_absolute_url())
        self.assertContains(response, staffer.profile.title)
        cur_post = staffer.positions.first()
        prev_post = staffer.positions.all()[1]
        self.assertContains(response, cur_post.title)
        self.assertContains(response, prev_post.title)
        self.assertContains(response, prev_post.years)
        self.assertNotContains(response, cur_post.years)

        # co-authored a blog post with staffer
        staffer2 = Person.objects.get(username='staff2')
        solo_post = staffer.blogposts.last()
        coauth_post = staffer2.blogposts.first()
        self.assertContains(response, solo_post.title)  # show both blog posts
        self.assertContains(response, solo_post.title)
        # indicate that one post has another author
        self.assertContains(response, staffer2.profile.title)

        response = self.client.get(staffer2.get_absolute_url())
        # only posts from this author
        self.assertNotContains(response, solo_post.title)
        self.assertContains(response, coauth_post.title)
        self.assertContains(response, staffer.profile.title)

        # published but not is_staff
        staffer.profile.is_staff = False
        staffer.profile.save()
        assert self.client.get(staffer.get_absolute_url()).status_code == 404

        # not published - should 404
        staffer.profile.status = CONTENT_STATUS_DRAFT
        staffer.profile.is_staff = True
        staffer.profile.save()
        assert self.client.get(staffer.get_absolute_url()).status_code == 404


class TestProfileSitemap(TestCase):
    fixtures = ['test_people_data.json']

    def test_items(self):
        sitemap_items = ProfileSitemap().items()

        published_staff = Profile.objects.filter(is_staff=True).published()
        for profile in published_staff:
            assert profile in sitemap_items

        published_non_staff = Profile.objects.filter(
            is_staff=False).published()
        for profile in published_non_staff:
            assert profile not in sitemap_items
