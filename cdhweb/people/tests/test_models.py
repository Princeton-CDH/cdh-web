import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock

from cdhweb.projects.models import Membership, Role
from cdhweb.people.models import Person, Position, Title, init_person_from_ldap
from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.core.models import Page
from cdhweb.pages.models import HomePage
from cdhweb.projects.models import ProjectsLandingPage, Project, Grant, GrantType


class TestTitle(TestCase):

    def setUp(self):
        """create a person and title for testing"""
        self.tom = Person.objects.create(first_name="tom")
        self.director = Title.objects.create(title="director")

    def test_num_people(self):
        """title should track how many people hold it"""
        # initially no one has the title
        assert self.director.num_people() == 0

        # give tom the title, should have 1 as num_people
        Position.objects.create(
            person=self.tom, title=self.director, start_date=date.today())
        assert self.director.num_people() == 1


class TestPosition(TestCase):

    def test_str(self):
        """position should be identified by person, title, and start year"""
        tom = Person.objects.create(first_name="tom")
        director = Title.objects.create(title="director")
        position = Position.objects.create(
            person=tom, title=director, start_date=date(2021, 1, 1))
        assert str(position) == "tom director (2021)"


class TestPerson:

    def test_current_title(self, staffer):
        """person should track its currently held title, if any"""
        # should return None if no positions
        person = Person.objects.create(last_name="smith")
        assert person.current_title is None

        # should return latest position if one exists
        assert staffer.current_title.title == "Research Software Engineer"

        # delete current position; should return None since none are active
        staffer.positions.first().delete()
        assert staffer.current_title is None

    def test_str(self, db):
        """person should be identified by first/last name, username, or pk"""
        self.person = Person.objects.create()

        # if no associated user or names, should use pk
        assert str(self.person) == f"Person {self.person.pk}"

        # if only associated user, should use username
        User = get_user_model()
        self.person.user = User.objects.create(username="user")
        assert str(self.person) == "user"

        # first name only
        self.person.first_name = "tom"
        assert str(self.person) == "tom"

        # last name only
        self.person.first_name = ""
        self.person.last_name = "jones"
        assert str(self.person) == "jones"

        # both names
        self.person.first_name = "tom"
        assert str(self.person) == "tom jones"

    def test_lastname_first(self, db):
        self.person = Person.objects.create()

        # first name only
        self.person.first_name = "Tom"
        assert self.person.lastname_first == "Tom"

        # last name only
        self.person.first_name = ""
        self.person.last_name = "Jones"
        assert self.person.lastname_first == "Jones"

        # both names
        self.person.first_name = "Tom"
        assert self.person.lastname_first == "Jones, Tom"

    def test_lt(self):
        # less than comparison based on lastname, firstname
        able_j = Person(last_name='Able', first_name='Jim')
        able_b = Person(last_name='Able', first_name='Bean')
        assert able_b < able_j
        assert not able_j < able_b

    def test_latest_grant(self, db, projects_landing_page):
        """person should track the most recent grant they were director on"""
        # setup
        project = Project(title="Project")
        projects_landing_page.add_child(instance=project)
        projects_landing_page.save()
        person = Person.objects.create()
        director = Role.objects.get_or_create(title="Project Director")[0]
        pm = Role.objects.get_or_create(title="Project Manager")[0]
        dcg = GrantType.objects.get_or_create(grant_type="Dataset Curation")[0]
        grant1 = Grant.objects.create(project=project, grant_type=dcg,
            start_date=date(2016, 5, 1), end_date=date(2016, 9, 30))
        grant2 = Grant.objects.create(project=project, grant_type=dcg,
            start_date=date(2017, 1, 1), end_date=date(2017, 5, 31))

        # no memberships = no latest grant
        assert person.latest_grant is None

        # current grant but not project director = no latest grant
        mship = Membership.objects.create(person=person, role=pm, project=project,
            start_date=date(2016, 5, 1), end_date=date(2016, 9, 30))
        assert person.latest_grant is None

        # project director on older grant; should return older grant as latest
        mship.role = director
        mship.save()
        assert person.latest_grant == grant1

        # project director on most recent grant; should return as latest
        mship.start_date = date(2017, 1, 1)
        mship.end_date = date(2017, 5, 31)
        mship.save()
        assert person.latest_grant == grant2

        # project director on both grants; should return newer one
        mship2 = Membership.objects.create(person=person, role=director,
            project=project, start_date=date(2016, 5, 1),
            end_date=date(2016, 9, 30))
        assert person.latest_grant == grant2

        # project directorship with no end date; should count as latest
        mship2.delete()
        mship.end_date = None
        mship.save()
        assert person.latest_grant == grant2

        # project director on grant with no end date; should count as latest
        mship.end_date = date(2017, 5, 31)
        mship.save()
        grant2.end_date = None
        grant2.save()
        assert person.latest_grant == grant2

def test_profile_url(student, staffer, staffer_profile, faculty_pi):
    # student fixture has neither profile nor website link
    assert not student.profile_url
    # faculty pi has a profile url
    assert faculty_pi.profile_url == 'example.com'
    # staff person has local profile
    assert staffer.profile_url == staffer_profile.get_url()
    # unpublish; should be no more profile url
    staffer_profile.unpublish()
    assert not staffer.profile_url


class TestPersonQuerySet(TestCase):

    def setUp(self):
        """create testing data"""
        # create titles and roles
        self.director = Title.objects.create(title="director", sort_order=0)
        self.dev = Title.objects.create(title="developer", sort_order=1)
        self.data = Title.objects.create(title="data worker", sort_order=2)
        self.grad = Title.objects.create(
            title="Graduate Assistant", sort_order=2)
        self.undergrad = Title.objects.create(
            title="Undergraduate Assistant", sort_order=3)
        self.pgra = Title.objects.create(
            title="Postgraduate Research Associate")
        self.exec = Title.objects.get_or_create(
            title="Executive Committee Member")[0]
        self.sits_exec = Title.objects.get_or_create(
            title="Sits with Executive Committee")[0]
        self.proj_dir = Role.objects.create(title="Project Director")
        self.co_pi = Role.objects.create(title="Co-PI: Research Lead")
        self.pm = Role.objects.create(title="Project Manager")
        # FIXME should use fixtures when these are converted
        root = Page.objects.first()
        home = HomePage(title="home", slug="")
        root.add_child(instance=home)
        root.save()
        link = ProjectsLandingPage(title="projects", slug="projects",
                                   tagline="let's collaborate")
        home.add_child(instance=link)
        home.save()
        self.project = Project(title="project")
        link.add_child(instance=self.project)
        link.save()

    def test_staff(self):
        """should be able to filter people to only cdh staff"""
        tom = Person.objects.create(first_name="tom", cdh_staff=True)
        sam = Person.objects.create(first_name="sam")
        jim = Person.objects.create(first_name="jim")
        staff = Person.objects.cdh_staff()
        assert tom in staff
        assert sam not in staff
        assert jim not in staff

    def test_current(self):
        """should be able to filter to people with current positions"""
        # no position - should not be in current
        tom = Person.objects.create(first_name="tom")
        assert tom not in Person.objects.current()

        # add current position - no end date
        tom_director = Position.objects.create(person=tom, title=self.director,
                                               start_date=date.today())
        assert tom in Person.objects.current()

        # end date in future also considered current
        tom_director.end_date = date.today() + timedelta(weeks=20)
        tom_director.save()
        assert tom in Person.objects.current()

        # previous position = not current
        tom_director.delete()
        Position.objects.create(person=tom, title=self.dev,
                                start_date=date.today() - timedelta(weeks=50),
                                end_date=date.today() - timedelta(weeks=20))
        assert tom not in Person.objects.current()

        # past project director is not current
        tom_proj_dir = Membership.objects.create(project=self.project,
                                                 role=self.proj_dir, person=tom,
                                                 start_date=date.today() - timedelta(weeks=50),
                                                 end_date=date.today() - timedelta(weeks=20))
        assert tom not in Person.objects.current()

        # no end date on membership = current
        tom_proj_dir.end_date = None
        tom_proj_dir.save()
        assert tom in Person.objects.current()

        # end date in future = current
        tom_proj_dir.end_date = date.today() + timedelta(days=30)
        tom_proj_dir.save()
        assert tom in Person.objects.current()

        # end today = still current
        tom_proj_dir.end_date = date.today()
        tom_proj_dir.save()
        assert tom in Person.objects.current()

        # past project manager is not current
        tom_proj_dir.delete()
        tom_pm = Membership.objects.create(project=self.project, person=tom,
                                           role=self.pm, start_date=date.today() - timedelta(weeks=50),
                                           end_date=date.today() - timedelta(weeks=20))
        assert tom not in Person.objects.current()

        # current project manager is current
        tom_pm.end_date = date.today() + timedelta(days=30)
        tom_pm.save()
        assert tom in Person.objects.current()

        # end today = still current
        tom_pm.end_date = date.today()
        tom_pm.save()
        assert tom in Person.objects.current()

    def test_order_by_position(self):
        """should be able to order people by their position title rank"""
        # create some people
        tom = Person.objects.create(first_name="tom")
        sam = Person.objects.create(first_name="sam")
        jim = Person.objects.create(first_name="jim")
        deb = Person.objects.create(first_name="deb")

        # assign roles
        Position.objects.create(person=tom, title=self.director,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=sam, title=self.dev,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=jim, title=self.dev,
                                start_date=date.today() - timedelta(weeks=20))
        Position.objects.create(person=deb, title=self.data,
                                start_date=date.today() - timedelta(weeks=30))

        # sort by position title order; ties broken by earliest start date
        people = Person.objects.order_by_position()
        assert people[0] == tom
        assert people[1] == sam
        assert people[2] == jim
        assert people[3] == deb

    def test_student_affiliates(self):
        """should be able to filter people to student affiliates"""
        # create some people
        tom = Person.objects.create(first_name="tom", cdh_staff=True)
        sam = Person.objects.create(
            first_name="sam", cdh_staff=True, pu_status="graduate")
        jim = Person.objects.create(
            first_name="jim", cdh_staff=True, pu_status="undergraduate")
        deb = Person.objects.create(first_name="deb", pu_status="graduate")
        ada = Person.objects.create(first_name="ada", pu_status="graduate")
        eli = Person.objects.create(first_name="eli", cdh_staff=True)

        # add various roles and memberships
        Position.objects.create(person=tom, title=self.director,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=sam, title=self.grad,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=jim, title=self.undergrad,
                                start_date=date.today() - timedelta(weeks=30))
        Membership.objects.create(person=deb, project=self.project,
                                  role=self.proj_dir,
                                  start_date=date.today() - timedelta(weeks=30))
        Membership.objects.create(person=ada, project=self.project,
                                  role=self.pm,
                                  start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=eli, title=self.pgra,
                                start_date=date.today() - timedelta(weeks=30))

        # director (cdh staff) is not a student affiliate
        assert tom not in Person.objects.student_affiliates()

        # grad assistant (cdh staff) is a student affiliate
        assert sam in Person.objects.student_affiliates()

        # undergrad assistant (cdh staff) is a student affiliate
        assert jim in Person.objects.student_affiliates()

        # graduate PI (project director) is a student affiliate
        assert deb in Person.objects.student_affiliates()

        # graduate PM (project manager) is a student affiliate
        assert ada in Person.objects.student_affiliates()

        # PGRA (cdh staff) is a student affiliate
        assert eli in Person.objects.student_affiliates()

        # removing memberships ends affiliation for grad PI/PM
        Membership.objects.all().delete()
        assert deb not in Person.objects.student_affiliates()
        assert ada not in Person.objects.student_affiliates()

    def test_affiliates(self):
        """should be able to filter people to faculty affiliates"""
        # create some people
        tom = Person.objects.create(first_name="tom", pu_status="fac")
        sam = Person.objects.create(first_name="sam", pu_status="fac")
        jim = Person.objects.create(first_name="jim", pu_status="stf")
        deb = Person.objects.create(first_name="deb", pu_status="graduate")
        ada = Person.objects.create(first_name="ada", cdh_staff=True)

        # add various roles and memberships
        Membership.objects.create(person=tom, project=self.project,
                                  role=self.proj_dir,
                                  start_date=date.today() - timedelta(weeks=30))
        Membership.objects.create(person=sam, project=self.project,
                                  role=self.co_pi,
                                  start_date=date.today() - timedelta(weeks=30))
        Membership.objects.create(person=jim, project=self.project,
                                  role=self.proj_dir,
                                  start_date=date.today() - timedelta(weeks=30))
        Membership.objects.create(person=deb, project=self.project,
                                  role=self.proj_dir,
                                  start_date=date.today() - timedelta(weeks=30))
        Membership.objects.create(person=ada, project=self.project,
                                  role=self.co_pi,
                                  start_date=date.today() - timedelta(weeks=30))

        # faculty who are project directors are affiliates
        assert tom in Person.objects.affiliates()

        # faculty who are co-PIs are affiliates
        assert sam in Person.objects.affiliates()

        # staff who are project directors are affiliates (e.g. PUL)
        assert jim in Person.objects.affiliates()

        # graduate PIs are not faculty affiliates (they're student affiliates)
        assert deb not in Person.objects.affiliates()

        # cdh staff are never affiliates
        assert ada not in Person.objects.affiliates()

    def test_executive_committee(self):
        """should be able to filter people to executive committee"""
        # create people
        tom = Person.objects.create(first_name="tom", pu_status="fac")
        sam = Person.objects.create(first_name="sam", pu_status="fac")
        jim = Person.objects.create(first_name="jim", pu_status="stf")

        # assign roles
        Position.objects.create(person=tom, title=self.director,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=sam, title=self.exec,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=jim, title=self.sits_exec,
                                start_date=date.today() - timedelta(weeks=30))

        # faculty director is not part of committee
        assert tom not in Person.objects.executive_committee()

        # current exec members are part of committee
        assert sam in Person.objects.executive_committee()

        # "sits with exec" people (incl. staff) are part of committee
        assert jim in Person.objects.executive_committee()

    def test_exec_member(self):
        # create people
        tom = Person.objects.create(first_name="tom", pu_status="fac")
        jim = Person.objects.create(first_name="jim", pu_status="stf")

        # assign roles
        Position.objects.create(person=tom, title=self.exec,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=jim, title=self.sits_exec,
                                start_date=date.today() - timedelta(weeks=30))

        # current exec members are exec members
        assert tom in Person.objects.exec_member()

        # "sits with exec" people are not exec members
        assert jim not in Person.objects.exec_member()

    def test_sits_with_exec(self):
        # create people
        tom = Person.objects.create(first_name="tom", pu_status="fac")
        jim = Person.objects.create(first_name="jim", pu_status="stf")

        # assign roles
        Position.objects.create(person=tom, title=self.exec,
                                start_date=date.today() - timedelta(weeks=30))
        Position.objects.create(person=jim, title=self.sits_exec,
                                start_date=date.today() - timedelta(weeks=30))

        # current exec members aren't "sits with"
        assert tom not in Person.objects.sits_with_exec()

        # "sits with exec" people are "sits with"
        assert jim in Person.objects.sits_with_exec()


class TestInitProfileFromLDAP(TestCase):

    def setUp(self):
        """create user and mock ldap data for testing"""
        # create user to test with
        User = get_user_model()
        self.staff_user = User.objects.create_user(username='staff',
                                                   email='STAFF@EXAMPLE.com')

        # use Mock to simulate ldap data provided by pucas
        self.ldapinfo = Mock(displayName='Joe E. Schmoe',
                             # no telephone or office set
                             telephoneNumber=[], street=[],
                             title='Freeloader, World at large', pustatus='stf',
                             ou='English')
        init_person_from_ldap(self.staff_user, self.ldapinfo)
        self.staff_person = Person.objects.get(user=self.staff_user)

    def test_email(self):
        """user email should be converted to lower case and added to person"""
        assert self.staff_user.email == "staff@example.com"
        assert self.staff_person.email == "staff@example.com"

    def test_person_created(self):
        """person should be created to match user"""
        assert self.staff_user.person == self.staff_person

    def test_names_added(self):
        """first and last name should be populated"""
        assert self.staff_person.first_name == "Joe"
        assert self.staff_person.last_name == "Schmoe"

    def test_fields_populated(self):
        """other fields should be populated from ldap data if it exists"""
        assert self.staff_person.job_title == "Freeloader"
        assert self.staff_person.phone_number == ""
        assert self.staff_person.office_location == ""
        assert self.staff_person.pu_status == "stf"
        assert self.staff_person.department == "English"

    def test_phone_office(self):
        """phone number and office location should be added if present"""
        self.ldapinfo.telephoneNumber = "4800"
        self.ldapinfo.street = "801B"
        init_person_from_ldap(self.staff_user, self.ldapinfo)
        staff_person = Person.objects.get(user=self.staff_user)
        assert staff_person.phone_number == "4800"
        assert staff_person.office_location == "801B"

    def test_no_clobber(self):
        """when updating from ldap, existing fields shouldn't be changed"""
        self.staff_person.job_title = "New Job"
        self.staff_person.department = "History"
        self.staff_person.save()
        init_person_from_ldap(self.staff_user, self.ldapinfo)
        staff_person = Person.objects.get(user=self.staff_user)
        assert staff_person.job_title == "New Job"
        assert staff_person.department == "History"
