from datetime import date, timedelta

import pytest

from cdhweb.pages.models import RelatedLinkType
from cdhweb.people.models import (PeopleLandingPage, Person, PersonRelatedLink,
                                  Position, Profile, Title)
from cdhweb.projects.models import Grant, GrantType, Membership, Project, Role


def create_person_with_position(position, start_date=None, end_date=None,
                                **person_opts):
    '''factory method to create person with position for fixtures'''
    position = Title.objects.get_or_create(title=position)[0]
    person = Person.objects.create(**person_opts)
    Position.objects.create(person=person, title=position,
                            start_date=start_date, end_date=end_date)
    return person


@pytest.fixture
def project(db, project_landing_page):
    """Empty project for use in testing people."""
    project = Project(title="project")
    project_landing_page.add_child(instance=project)
    project_landing_page.save()
    return project


@pytest.fixture
def staffer(db):
    '''fixture to create a staff person with two staff positions'''
    staff_person = create_person_with_position(
        'DH Developer',
        start_date=date(2016, 3, 1), end_date=date(2018, 3, 1),
        first_name='Staffer', cdh_staff=True, pu_status='stf')
    rse = Title.objects.get_or_create(title='Research Software Engineer')[0]
    # give the staffer a second position
    Position.objects.create(person=staff_person, title=rse,
                            start_date=date(2018, 3, 2))
    return staff_person


@pytest.fixture
def postdoc(db):
    '''fixture to create a postdoc person'''
    return create_person_with_position(
        'Postdoctoral Fellow',
        start_date=date(2018, 3, 1),
        first_name='Postdoc', cdh_staff=True, pu_status='stf')


@pytest.fixture
def student(db):
    '''fixture to create a student person record'''
    return create_person_with_position(
        'Undergraduate Assistant',
        start_date=date(2018, 3, 1),
        first_name='student', cdh_staff=True, pu_status='undergraduate')


@pytest.fixture
def grad_pi(db, projects_landing_page):
    person = Person.objects.create(
        first_name='Tom', cdh_staff=False, pu_status='graduate')
    project = Project(title='Chinese Exchange Poems')
    projects_landing_page.add_child(instance=project)
    projects_landing_page.save()
    project_director = Role.objects.get_or_create(title='Project Director')[0]
    Membership.objects.create(
        project=project, person=person, role=project_director,
        start_date=date(2015, 9, 1))
    dataset_curation = GrantType.objects.get_or_create(grant_type='Dataset Curation')[0]
    Grant.objects.create(grant_type=dataset_curation, project=project,
                         start_date=date(2015, 9, 1),
                         end_date=date.today() + timedelta(days=30))
    return person


@pytest.fixture
def grad_pm(db, projects_landing_page):
    person = Person.objects.create(first_name='Tom', cdh_staff=False,
        pu_status='graduate', email='tom@princeton.edu')
    project = Project(title='Reconstructing the Past')
    projects_landing_page.add_child(instance=project)
    projects_landing_page.save()
    project_manager = Role.objects.get_or_create(title='Project Manager')[0]
    Membership.objects.create(
        project=project, person=person, role=project_manager,
        start_date=date(2015, 9, 1))
    dataset_curation = GrantType.objects.get_or_create(grant_type='Dataset Curation')[0]
    Grant.objects.create(grant_type=dataset_curation, project=project,
                         start_date=date(2015, 9, 1),
                         end_date=date.today() + timedelta(days=30))
    return person


@pytest.fixture
def faculty_pi(db, projects_landing_page):
    person = Person.objects.create(
        first_name='Josh', cdh_staff=False, pu_status='fac')
    project = Project(title='MEP')
    projects_landing_page.add_child(instance=project)
    projects_landing_page.save()
    project_director = Role.objects.get_or_create(title='Project Director')[0]
    dataset_curation = GrantType.objects.get_or_create(
        grant_type='Dataset Curation')[0]
    Grant.objects.create(grant_type=dataset_curation, project=project,
                         start_date=date(2019, 9, 1),
                         end_date=date.today() + timedelta(days=30))
    Membership.objects.create(
        project=project, person=person, role=project_director,
        start_date=date(2016, 9, 1))
    website = RelatedLinkType.objects.get_or_create(name="Website")[0]
    PersonRelatedLink.objects.create(
        person=person, type=website, url="example.com")
    return person


@pytest.fixture
def staff_pi(db, projects_landing_page):
    person = Person.objects.create(
        first_name='Thomas', cdh_staff=False, pu_status='stf')
    project = Project(title='SVP')
    projects_landing_page.add_child(instance=project)
    projects_landing_page.save()
    project_director = Role.objects.get_or_create(title='Project Director')[0]
    dataset_curation = GrantType.objects.get_or_create(
        grant_type='Dataset Curation')[0]
    Grant.objects.create(grant_type=dataset_curation, project=project,
                         start_date=date(2020, 9, 1),
                         end_date=date.today() + timedelta(days=30))
    Membership.objects.create(
        project=project, person=person, role=project_director,
        start_date=date(2016, 9, 1))
    return person


@pytest.fixture
def faculty_exec(db):
    return create_person_with_position(
        'Executive Committee Member',
        start_date=date(2018, 3, 1),
        first_name='Anna', cdh_staff=False, pu_status='fac')


@pytest.fixture
def staff_exec(db):
    return create_person_with_position(
        'Sits with Executive Committee',
        start_date=date(2010, 3, 1),
        first_name='Jay', cdh_staff=False, pu_status='stf')


@pytest.fixture
def people_landing_page(db, homepage):
    """create a test people landing page underneath the homepage"""
    landing = PeopleLandingPage(
        title="people", slug="people", tagline="cdh people")
    homepage.add_child(instance=landing)
    homepage.save()
    return landing


@pytest.fixture
def staffer_profile(db, people_landing_page, staffer):
    """profile for a staff person"""
    profile = Profile(
        person=staffer,
        title="Staffer",
        education="Princeton University"
    )
    people_landing_page.add_child(instance=profile)
    people_landing_page.save()
    return profile
