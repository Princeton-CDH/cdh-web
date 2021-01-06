from datetime import date, timedelta
from unittest.mock import Mock

from cdhweb.projects.models import Project, Membership, Role
from cdhweb.people.models import Person, Position, Title, init_person_from_ldap
from django.contrib.auth import get_user_model
from django.test import TestCase


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


class TestPerson(TestCase):

    def setUp(self):
        """create person and user for testing"""
        User = get_user_model()
        self.user = User.objects.create_user(username="user")
        self.person = Person.objects.create()

    def test_current_title(self):
        """person should track its currently held title, if any"""
        # should return None if no positions
        assert self.person.current_title is None

        # should return None if no positions are active
        director = Title.objects.create(title="director")
        old_title = Position.objects.create(
            person=self.person, title=director, end_date=date.today(),
            start_date=date.today() - timedelta(weeks=6))
        assert self.person.current_title is None

        # should return latest position if one exists
        developer = Title.objects.create(title="developer")
        new_title = Position.objects.create(
            person=self.person, title=developer, end_date=None,
            start_date=date.today())
        assert self.person.current_title == developer

    def test_str(self):
        """person should be identified by first/last name, username, or pk"""
        # if no associated user or names, should use pk
        assert str(self.person) == f"Person {self.person.pk}"

        # if only associated user, should use username
        self.person.user = self.user
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


class TestPersonQuerySet(TestCase):

    def setUp(self):
        """create testing data"""
        # FIXME why is this necessary?
        Title.objects.all().delete()

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
        self.exec = Title.objects.create(title="Executive Committee Member",
            sort_order=5)
        self.sits_exec = Title.objects.create(sort_order=6,
            title="Sits with Executive Committee")
        self.proj_dir = Role.objects.create(title="Project Director")
        self.co_pi = Role.objects.create(title="Co-PI: Research Lead")
        self.pm = Role.objects.create(title="Project Manager")
        self.project = Project.objects.create(title="project")

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
        """user email should be converted to lower case"""
        assert self.staff_user.email == "staff@example.com"

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
