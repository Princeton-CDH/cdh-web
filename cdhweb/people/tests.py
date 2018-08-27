from datetime import date, timedelta
from unittest.mock import Mock

from django.urls import reverse
from django.test import TestCase
from django.utils.text import slugify
from mezzanine.core.models import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED
import pytest

from cdhweb.blog.models import BlogPost
from .models import Title, Person, Position, init_profile_from_ldap, Profile


@pytest.mark.django_db
class TestTitle(TestCase):
    fixtures = ['test_people_data.json']

    def test_num_people(self):
        # test counts against fixture data
        faculty_director = Title.objects.filter(title='Faculty Director').first()
        assert faculty_director.num_people() == 0
        lead_developer = Title.objects.filter(title='Lead Developer').first()
        assert lead_developer.num_people() == 1


@pytest.mark.django_db
class TestPerson(TestCase):

    def test_current_title(self):
        # create test person and add two positions
        staffer = Person.objects.create(username='staff')
        staff_title = Title.objects.create(title='staff')
        fellow = Title.objects.create(title='fellow')
        Position.objects.create(user=staffer, title=fellow,
            start_date='2015-01-01', end_date='2015-12-31')
        Position.objects.create(user=staffer, title=staff_title,
            start_date='2016-06-01')
        assert staffer.current_title == staff_title

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
        pers = Person.objects.create(username='foo', first_name='Jean', last_name='Jones')
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

    def test_is_staff(self):
        staffer = Person.objects.create(username='staffer')
        staff_profile = Profile.objects.create(user=staffer, is_staff=True)
        grad = Person.objects.create(username='grad')
        grad_profile = Profile.objects.create(user=grad, is_staff=False)

        staff = Profile.objects.all().staff()
        assert staff.count() == 1
        assert staff_profile in staff
        assert grad_profile not in staff

    def test_current(self):
        staffer = Person.objects.create(username='staffer')
        staff_profile = Profile.objects.create(user=staffer)
        staff_title = Title.objects.create(title='staff')
        postdoc = Title.objects.create(title='post-doc')
        # previous post
        prev_post = Position.objects.create(user=staffer, title=postdoc,
            start_date='2015-01-01', end_date='2015-12-31')

        assert not Profile.objects.all().current().exists()

        # current post - no end date
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date='2016-06-01')
        current_profiles = Profile.objects.all().current()
        assert current_profiles.exists()
        assert staff_profile in current_profiles

        # end date in future also considered current
        cur_post.end_date = date.today() + timedelta(days=30)
        cur_post.save()
        assert current_profiles.exists()
        assert staff_profile in current_profiles

    def test_not_current(self):
        # current staff person
        staffer = Person.objects.create(username='staffer')
        staff_profile = Profile.objects.create(user=staffer)
        staff_title = Title.objects.create(title='staff')
        # current post - no end date
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date='2016-06-01')

        assert not Profile.objects.all().not_current().exists()

        # past fellow
        fellow = Person.objects.create(username='fellow')
        fellow_profile = Profile.objects.create(user=fellow)
        postdoc = Title.objects.create(title='post-doc')
        # previous post
        prev_post = Position.objects.create(user=fellow, title=postdoc,
            start_date='2015-01-01', end_date='2015-12-31')
        not_current = Profile.objects.all().not_current()
        assert not_current.exists()
        assert fellow_profile in not_current
        assert staff_profile not in not_current

        # end date in future also considered current
        cur_post.end_date = date.today() + timedelta(days=30)
        cur_post.save()
        assert not_current.exists()
        assert staff_profile not in not_current

    def test_order_by_position(self):
        director_title = Title.objects.create(title='director', sort_order=1)
        staff_title = Title.objects.create(title='staff', sort_order=2)

        director = Person.objects.create(username='director')
        director_profile = Profile.objects.create(user=director)
        Position.objects.create(user=director, title=director_title,
            start_date='2016-06-01')

        staffer = Person.objects.create(username='staffer')
        staff_profile = Profile.objects.create(user=staffer)
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date='2016-06-01')

        profiles = Profile.objects.all().order_by_position()
        # sort by position title order
        assert director_profile == profiles[0]
        assert staff_profile == profiles[1]

        # second staffer with later start
        staffer2 = Person.objects.create(username='staffer2')
        staff2_profile = Profile.objects.create(user=staffer2)
        Position.objects.create(user=staffer2, title=staff_title,
            start_date='2016-12-01')
        profiles = Profile.objects \
            .filter(user__positions__title__title='staff').order_by_position()
        # should sort by start date, earliest first
        assert staff_profile == profiles[0]
        assert staff2_profile == profiles[1]


class TestPosition(TestCase):

    def test_str(self):
        staff_title = Title.objects.create(title='staff', sort_order=2)
        director = Person.objects.create(username='director')
        pos = Position.objects.create(user=director, title=staff_title,
            start_date=date.today())

        assert str(pos) == '%s %s (%s)' % (director, staff_title,
                                           pos.start_date.year)

    def test_is_current(self):
        staff_title = Title.objects.create(title='staff', sort_order=2)
        director = Person.objects.create(username='director')

        # start date in past, no end date
        pos = Position(user=director, title=staff_title,
            start_date=date.today() - timedelta(days=50))
        assert pos.is_current

        # end date in future
        pos.end_date = date.today() + timedelta(days=30)
        assert pos.is_current

        # end date in past
        pos.end_date = date.today() - timedelta(days=3)
        assert not pos.is_current

        # start date in future
        pos.start_date = date.today() + timedelta(days=3)
        assert not pos.is_current

    def test_years(self):
        staff_title = Title.objects.create(title='staff', sort_order=2)
        director = Person.objects.create(username='director')

        # start date in past, no end date
        pos = Position(user=director, title=staff_title,
                start_date=date(2016, 6, 1))

        # no end date
        assert pos.years == '2016–'
        # end date same year as start
        pos.end_date = date(2016, 12, 1)
        assert pos.years == '2016'

        # end date known, different year
        pos.end_date = date(2017, 12, 1)
        assert pos.years == '2016–2017'



@pytest.mark.django_db
def test_init_profile_from_ldap():
    # create user to test with
    staffer = Person.objects.create(username='staff',
        email='STAFF@EXAMPLE.com')

    # use Mock to simulate ldap data provided by pucas
    ldapinfo = Mock(displayName='Joe E. Schmoe',
        # no telephone or office set
        telephoneNumber=[], street=[],
        title='Freeloader, World at large') # job title, organizational unit

    init_profile_from_ldap(staffer, ldapinfo)
    updated_staffer = Person.objects.get(username='staff')
    # email should be converted to lower case
    assert updated_staffer.email == staffer.email.lower()
    # profile should have been created
    assert updated_staffer.profile
    profile = updated_staffer.profile
    # profile fields should be autopopulated where content exists
    assert profile.title == ldapinfo.displayName
    assert profile.slug == slugify(ldapinfo.displayName)
    assert profile.phone_number == ''
    assert profile.office_location == ''
    assert profile.status == CONTENT_STATUS_DRAFT
    # title should be created
    assert Title.objects.filter(title='Freeloader').exists()

    # ldap info with telephone and street
    ldapinfo.telephoneNumber = '4800'
    ldapinfo.street = '801B'
    init_profile_from_ldap(staffer, ldapinfo)
    profile = Person.objects.get(username='staff').profile
    assert profile.phone_number == ldapinfo.telephoneNumber
    assert profile.office_location == ldapinfo.street
    # title should not be duplicated
    assert Title.objects.filter(title='Freeloader').count() == 1


class TestViews(TestCase):

    def test_staff_redirect(self):
        # valid id gives permanent redirect to slug url
        slug = 'claus-the-chicken'
        response = self.client.get('/about/staff/%s/' % slug)
        assert response.status_code == 301   # moved permanently
        assert response.url == reverse('people:profile', kwargs={'slug': slug})

    def test_staff_list(self):
        # create test person and add two positions
        staffer = Person.objects.create(username='staff')
        profile = Profile.objects.create(user=staffer, title='Amazing Contributor',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True)
        staff_title = Title.objects.create(title='staff')
        fellow = Title.objects.create(title='fellow')
        postdoc = Title.objects.create(title='post-doc')
        prev_post = Position.objects.create(user=staffer, title=postdoc,
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31))
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date=date(2016, 6,1))

        response = self.client.get(reverse('people:staff'))
        # person should only appear once even if they have multiple positions
        assert len(response.context['object_list']) == 1

        self.assertContains(response, profile.title)
        self.assertContains(response, profile.current_title)
        self.assertContains(response, profile.get_absolute_url())
        self.assertNotContains(response, prev_post.title)
        self.assertNotContains(response, prev_post.years)
        self.assertNotContains(response, cur_post.years)

        # should be listed if position end date is set for future
        cur_post.end_date = date.today() + timedelta(days=1)
        cur_post.save()
        response = self.client.get(reverse('people:staff'))
        assert profile in response.context['object_list']
        # should not be listed if position end date has passed
        cur_post.end_date = date.today() - timedelta(days=1)
        cur_post.save()
        response = self.client.get(reverse('people:staff'))
        assert profile not in response.context['object_list']

    def test_alumni_list(self):
        # create test person and add two positions
        staffer = Person.objects.create(username='staff')
        profile = Profile.objects.create(user=staffer, title='Amazing Contributor',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True)
        staff_title = Title.objects.create(title='staff')
        fellow = Title.objects.create(title='fellow')
        postdoc = Title.objects.create(title='post-doc')
        prev_post = Position.objects.create(user=staffer, title=postdoc,
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31))
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date=date(2016, 6, 1))

        alum = Person.objects.create(username='oldstaff')
        alum_profile = Profile.objects.create(user=alum, title='Past Brilliance',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True)
        alum_post = Position.objects.create(user=alum, title=postdoc,
            start_date=date(2015, 1, 1), end_date=date(2016, 2, 28))
        prev_alum_post = Position.objects.create(user=alum, title=fellow,
            start_date=date(2014, 1, 1), end_date=date(2014, 12, 31))

        response = self.client.get(reverse('people:alumni'))
        # person should only appear once even if they have multiple positions
        assert len(response.context['object_list']) == 1

        self.assertContains(response, alum_profile.title)
        self.assertContains(response, alum_post.title)
        self.assertContains(response, alum_post.years)
        self.assertContains(response, alum_profile.get_absolute_url())

    def test_profile_detail(self):
         # create test person and add two positions
        staffer = Person.objects.create(username='staff')
        profile = Profile.objects.create(user=staffer, title='Amazing Contributor',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True, slug='staffer')
        staff_title = Title.objects.create(title='staff')
        fellow = Title.objects.create(title='fellow')
        postdoc = Title.objects.create(title='post-doc')
        prev_post = Position.objects.create(user=staffer, title=postdoc,
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31))
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date=date(2016, 6,1))

        response = self.client.get(reverse('people:profile', args=[profile.slug]))
        self.assertContains(response, profile.title)
        self.assertContains(response, cur_post.title)
        self.assertContains(response, prev_post.title)
        self.assertContains(response, prev_post.years)
        self.assertNotContains(response, cur_post.years)

        # create another person and make some blog posts that belong to the people
        staffer2 = Person.objects.create(username='staff2')
        profile2 = Profile.objects.create(user=staffer2, title='Great Writer',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True, slug='staffer2')
        post = BlogPost.objects.create(title='Solo blog post')
        post2 = BlogPost.objects.create(title='Collaborative blog post')
        post.users.add(staffer) # written by one user
        post2.users.add(staffer, staffer2) # written by two users together

        response = self.client.get(reverse('people:profile', args=[profile.slug]))
        self.assertContains(response, post.title) # show both blog posts
        self.assertContains(response, post2.title)
        self.assertContains(response, profile2.title) # indicate that one post has another author
        response = self.client.get(reverse('people:profile', args=[profile2.slug]))
        self.assertNotContains(response, post.title) # only posts from this author
        self.assertContains(response, post2.title)
        self.assertContains(response, profile.title)