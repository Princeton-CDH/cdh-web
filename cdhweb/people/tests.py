from datetime import date, timedelta
from unittest.mock import Mock

from django.urls import reverse
from django.test import TestCase
from django.utils.text import slugify
from mezzanine.core.models import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED
import pytest

from cdhweb.blog.models import BlogPost
from cdhweb.people.models import Title, Person, Position, \
    init_profile_from_ldap, Profile
from cdhweb.projects.models import Project, Grant, GrantType, Role, Membership
from cdhweb.resources.models import ResourceType, UserResource


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
        UserResource.objects.create(user=pers, resource_type=website,
                                    url=ext_profile_url)
        assert pers.website_url == ext_profile_url

    def test_profile_url(self):
        pers = Person.objects.create(username='foo')
        # no urls
        assert pers.profile_url is None

        # add a website url resource
        website = ResourceType.objects.get_or_create(name='Website')[0]
        ext_profile_url = 'http://person.me'
        UserResource.objects.create(user=pers, resource_type=website,
                                    url=ext_profile_url)
        assert pers.profile_url == ext_profile_url

        # add local profile - takes precedence over external
        profile = Profile.objects.create(user=pers, is_staff=True, slug='foo',
                                         status=CONTENT_STATUS_PUBLISHED)

        # non-staff profile, should fall back to external
        profile.is_staff = False
        profile.save()
        assert pers.profile_url == ext_profile_url


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

        staff = Profile.objects.staff()
        assert staff.count() == 1
        assert staff_profile in staff
        assert grad_profile not in staff

    def test_current(self):
        staffer = Person.objects.create(username='staffer')
        staff_profile = Profile.objects.create(user=staffer)
        staff_title = Title.objects.create(title='staff')
        postdoc = Title.objects.create(title='post-doc')
        # no position - should not be in current
        assert not Profile.objects.current().exists()
        # previous post
        Position.objects.create(user=staffer, title=postdoc,
                                start_date='2015-01-01', end_date='2015-12-31')
        assert not Profile.objects.current().exists()

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

        staff_profile.delete()

        # affiliate with current grant project
        grad = Person.objects.create(username='tom', first_name='Tom')
        grad_profile = Profile.objects.create(user=grad, pu_status='graduate')
        # graduate flag but no project
        assert grad_profile not in Profile.objects.current()
        # project role but not director
        gradproj = Project.objects.create(title='Chinese Exchange Poems')
        researcher = Role.objects.create(title='Researcher')
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=gradproj, grant_type=grtype,
                                     start_date='2015-01-01')
        Membership.objects.create(project=gradproj, user=grad, grant=grant,
                                  role=researcher)
        assert grad_profile not in Profile.objects.current()

        # set as projext director on the same current grant
        proj_director = Role.objects.create(title='Project Director')
        Membership.objects.create(project=gradproj, user=grad, grant=grant,
                                  role=proj_director)
        assert grad_profile in Profile.objects.current()

        # end date in future also considered current
        cur_post.end_date = date.today() + timedelta(days=30)
        cur_post.save()
        assert grad_profile in Profile.objects.current()
        # set grant end date to past - no longer current
        cur_post.end_date = date.today() - timedelta(days=30)
        cur_post.save()
        assert grad_profile in Profile.objects.current()

        # end today = still current
        cur_post.end_date = date.today()
        cur_post.save()
        assert grad_profile in Profile.objects.current()

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

        profiles = Profile.objects.order_by_position()
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

    def test_postdocs(self):
        # create test person
        postdoc = Person.objects.create(username='nora')
        postdoc_profile = Profile.objects.create(user=postdoc)
        # no position, not in postdoc filter
        assert postdoc_profile not in Profile.objects.postdocs()

        # add position, should be in postdoc filter
        postdoc_title = Title.objects.get_or_create(title='Postdoctoral Fellow')[0]
        Position.objects.create(user=postdoc, title=postdoc_title,
            start_date='2016-12-01')
        assert postdoc_profile in Profile.objects.postdocs()

    def test_not_postdocs(self):
        # create test person
        postdoc = Person.objects.create(username='jim')
        postdoc_profile = Profile.objects.create(user=postdoc)
        # no position, should be in not-postdoc filter
        assert postdoc_profile in Profile.objects.not_postdocs()

        # add position, should no longer be in not-postdoc filter
        postdoc_title = Title.objects.get_or_create(title='Postdoctoral Fellow')[0]
        Position.objects.create(user=postdoc, title=postdoc_title,
            start_date='2016-12-01')
        assert postdoc_profile not in Profile.objects.not_postdocs()

    def test_students(self):
        # test student profile filter

        # staff person - not student
        staffer = Person.objects.create(username='staffer')
        staff_profile = Profile.objects.create(user=staffer)
        staff_title = Title.objects.create(title='staff')
        Position.objects.create(user=staffer, title=staff_title,
                                start_date='2016-06-01')
        assert staff_profile not in Profile.objects.students()

        # grad, undergrad assistant
        grad = Person.objects.create(username='grad')
        grad_profile = Profile.objects.create(user=grad)
        grad_title = Title.objects.create(title='Graduate Assistant')
        Position.objects.create(user=grad, title=grad_title,
                                start_date='2016-06-01')
        undergrad = Person.objects.create(username='undergrad')
        undergrad_profile = Profile.objects.create(user=undergrad)
        undergrad_title = Title.objects.create(title='Undergraduate Assistant')
        Position.objects.create(user=undergrad, title=undergrad_title,
                                start_date='2016-06-01')
        assert grad_profile in Profile.objects.students()
        assert undergrad_profile in Profile.objects.students()

        # person with student status with a project
        grad2 = Person.objects.create(username='tom')
        grad2_profile = Profile.objects.create(user=grad2, pu_status='graduate')
        # graduate flag but no project
        assert grad2_profile not in Profile.objects.students()
        # project role but not director
        gradproj = Project.objects.create(title='Chinese Exchange Poems')
        researcher = Role.objects.create(title='Researcher')
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=gradproj, grant_type=grtype,
            start_date='2015-01-1', end_date='2016-01-01')
        Membership.objects.create(project=gradproj,
            user=grad2, grant=grant, role=researcher)
        assert grad2_profile not in Profile.objects.students()

        # project director
        proj_director = Role.objects.create(title='Project Director')
        Membership.objects.create(project=gradproj,
            user=grad2, grant=grant, role=proj_director)

        assert grad2_profile in Profile.objects.students()

        # also valid with undergrad flag
        grad2_profile.pu_status = 'undergraduate'
        grad2_profile.save()
        assert grad2_profile in Profile.objects.students()

        # but not with anything else
        grad2_profile.pu_status = 'stf'
        grad2_profile.save()
        assert grad2_profile not in Profile.objects.students()


class TestPosition(TestCase):

    def test_str(self):
        staff_title = Title.objects.create(title='staff', sort_order=2)
        director = Person.objects.create(username='director')
        pos = Position.objects.create(user=director, title=staff_title,
            start_date=date.today())

        assert str(pos) == '%s %s (%s)' % (director, staff_title,
                                           pos.start_date.year)


@pytest.mark.django_db
def test_init_profile_from_ldap():
    # create user to test with
    staffer = Person.objects.create(username='staff',
        email='STAFF@EXAMPLE.com')

    # use Mock to simulate ldap data provided by pucas
    ldapinfo = Mock(displayName='Joe E. Schmoe',
        # no telephone or office set
        telephoneNumber=[], street=[],
        title='Freeloader, World at large', pustatus='stf')
        # job title, organizational unit

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
    assert profile.pu_status == 'stf'
    assert profile.status == CONTENT_STATUS_DRAFT
    # title should be created
    assert Title.objects.filter(title='Freeloader').exists()

    # when updating, profile status and existing fields should not change
    new_title = 'Somebody Else'
    profile.title = new_title
    profile.status = CONTENT_STATUS_PUBLISHED
    profile.save()
    init_profile_from_ldap(staffer, ldapinfo)
    assert profile.title == new_title
    assert profile.status == CONTENT_STATUS_PUBLISHED

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
        profile = Profile.objects.create(
            user=staffer, title='Amazing Contributor',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True)
        staff_title = Title.objects.create(title='staff')
        assoc = Title.objects.create(title='Associate')
        prev_post = Position.objects.create(
            user=staffer, title=assoc,
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31))
        cur_post = Position.objects.create(
            user=staffer, title=staff_title, start_date=date(2016, 6, 1))

        # postdoc with is staff should not be listed
        postdoc = Person.objects.create(username='postdoc')
        postdoc_profile = Profile.objects.create(
            user=postdoc, status=CONTENT_STATUS_PUBLISHED, is_staff=True)
        postdoc_title = Title.objects.get_or_create(title='Postdoctoral Fellow')[0]
        Position.objects.create(user=postdoc, title=postdoc_title,
                                start_date=date(2015, 1, 1))

        response = self.client.get(reverse('people:staff'))
        # person should only appear once even if they have multiple positions
        assert len(response.context['current']) == 1

        # staffer profile should be included
        assert profile in response.context['current']
        # postdoc profile should not
        assert postdoc_profile not in response.context['current']

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
        assert profile in response.context['current']
        # should be in past, not current, if position end date has passed
        cur_post.end_date = date.today() - timedelta(days=1)
        cur_post.save()
        response = self.client.get(reverse('people:staff'))
        assert profile not in response.context['current']
        assert profile in response.context['past']

        # should link to other people pages
        self.assertContains(response, reverse('people:postdocs'))
        self.assertContains(response, reverse('people:students'))

    def test_postdoc_list(self):
        postdoc = Person.objects.create(username='postdoc')
        postdoc_profile = Profile.objects.create(
            user=postdoc, status=CONTENT_STATUS_PUBLISHED, is_staff=True,
            slug='postdoc')
        postdoc_title = Title.objects.get_or_create(title='Postdoctoral Fellow')[0]
        Position.objects.create(user=postdoc, title=postdoc_title,
                                start_date=date(2015, 1, 1))

        response = self.client.get(reverse('people:postdocs'))
        # person should only appear once even if they have multiple positions
        assert len(response.context['current']) == 1
        # postdoc profile should be included
        assert postdoc_profile in response.context['current']

        self.assertContains(response, postdoc_profile.title)
        self.assertContains(response, postdoc_profile.current_title)
        self.assertContains(response, postdoc_profile.get_absolute_url())

    def test_student_list(self):
        # grad, undergrad assistant
        grad = Person.objects.create(username='grad')
        grad_profile = Profile.objects.create(
            user=grad, slug='grad', is_staff=True, title='Graduate Student',
            status=CONTENT_STATUS_PUBLISHED)
        grad_title = Title.objects.create(title='Graduate Assistant')
        Position.objects.create(user=grad, title=grad_title,
                                start_date='2016-06-01')
        undergrad = Person.objects.create(username='undergrad')
        undergrad_profile = Profile.objects.create(
            user=undergrad, slug='undergrad', is_staff=True,
            title='Undergraduate Student', status=CONTENT_STATUS_PUBLISHED)
        undergrad_title = Title.objects.create(title='Undergraduate Assistant')
        Position.objects.create(user=undergrad, title=undergrad_title,
                                start_date='2015-06-01', end_date='2016-06-01')

        # person with student status with a project
        grad_pi = Person.objects.create(username='tom')
        grad_pi_profile = Profile.objects.create(
            user=grad_pi, pu_status='graduate', title='Tom M.', slug='tom',
            is_staff=False, status=CONTENT_STATUS_PUBLISHED)
        # project director
        gradproj = Project.objects.create(title='Chinese Exchange Poems')
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=gradproj, grant_type=grtype,
                                     start_date='2015-01-1', end_date='2016-01-01')
        proj_director = Role.objects.create(title='Project Director')
        Membership.objects.create(project=gradproj, user=grad_pi,
                                  grant=grant, role=proj_director)

        response = self.client.get(reverse('people:students'))
        assert grad_profile in response.context['current']
        assert undergrad_profile in response.context['past']
        assert grad_pi_profile in response.context['past']

        # grad and undergrad have profile pages
        self.assertContains(response, grad_profile.title)
        self.assertContains(response, grad_profile.current_title)
        self.assertContains(response, grad_profile.get_absolute_url())
        self.assertContains(response, undergrad_profile.title)
        # undergrad has no current title, displays first title (with dates)
        self.assertContains(response, undergrad.positions.first().title)
        self.assertContains(response, undergrad_profile.get_absolute_url())
        # grad project director does not have local profile page or title
        self.assertContains(response, grad_pi_profile.title)
        self.assertNotContains(response, grad_pi_profile.get_absolute_url())

        # add a website url resource to grad pi
        website = ResourceType.objects.get_or_create(name='Website')[0]
        ext_profile_url = 'http://person.me'
        UserResource.objects.create(user=grad_pi, resource_type=website,
                                    url=ext_profile_url)
        assert grad_pi.profile_url == ext_profile_url
        response = self.client.get(reverse('people:students'))
        self.assertContains(response, grad_pi_profile.title)
        self.assertContains(response, ext_profile_url)

    def test_profile_detail(self):
         # create test person and add two positions
        staffer = Person.objects.create(username='staff')
        profile = Profile.objects.create(user=staffer, title='Amazing Contributor',
            status=CONTENT_STATUS_PUBLISHED, is_staff=True, slug='staffer')
        staff_title = Title.objects.create(title='staff')
        postdoc = Title.objects.create(title='post-doc')
        prev_post = Position.objects.create(user=staffer, title=postdoc,
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31))
        cur_post = Position.objects.create(user=staffer, title=staff_title,
            start_date=date(2016, 6,1))

        profile_url = reverse('people:profile', args=[profile.slug])
        response = self.client.get(profile_url)
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

        # published but not is_staff
        profile.is_staff = False
        profile.save()
        assert self.client.get(profile_url).status_code == 404

        # not published - should 404
        profile.status = CONTENT_STATUS_DRAFT
        profile.is_staff = True
        profile.save()
        assert self.client.get(profile_url).status_code == 404
