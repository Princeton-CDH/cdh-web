from datetime import date, timedelta
from unittest.mock import Mock

from cdhweb.people.models import (Person, Position, ProfilePage, Title,
                                  init_person_from_ldap)
from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (nested_form_data, rich_text,
                                           streamfield)


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
        new_title = Position.objects.create(
            person=self.person, title=director, end_date=None,
            start_date=date.today())
        assert self.person.current_title == "director"

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


class TestProfilePage(WagtailPageTests):
    pass


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
