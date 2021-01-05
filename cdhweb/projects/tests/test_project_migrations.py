from unittest import skip
from datetime import date

from cdhweb.resources.tests.test_utils import TestMigrations


class CalculateMembershipDates(TestMigrations):

    app = 'projects'
    migrate_from = '0010_add_membership_date_range'
    migrate_to = '0011_calculate_membership_dates'

    def setUpBeforeMigration(self, apps):

        Project = apps.get_model('projects', 'Project')
        Grant = apps.get_model('projects', 'Grant')
        GrantType = apps.get_model('projects', 'GrantType')
        Membership = apps.get_model('projects', 'Membership')
        Role = apps.get_model('projects', 'Role')
        User = apps.get_model('auth', 'User')
        Profile = apps.get_model('people', 'Profile')
        Position = apps.get_model('people', 'Position')
        Title = apps.get_model('people', 'Title')

        # create project to attach grants and members
        project = Project.objects.create(site_id=1)

        grant_type = GrantType.objects.all().first()
        grant1 = Grant.objects.create(
            project=project, grant_type=grant_type,
            start_date=date(2016, 9, 1), end_date=date(2017, 8, 30))
        grant2 = Grant.objects.create(
            project=project, grant_type=grant_type,
            start_date=date(2017, 9, 1), end_date=date(2018, 8, 30))
        # pi on both grants
        pi_role = Role.objects.create(title='Project Director')
        pi = User.objects.create(username='pi')
        Membership.objects.create(project=project, grant=grant1,
                                  role=pi_role, user=pi)
        Membership.objects.create(project=project, grant=grant2,
                                  role=pi_role, user=pi)
        # pm on first grant
        pm_role = Role.objects.create(title='Project Manager')
        pm = User.objects.create(username='pm')
        Membership.objects.create(project=project, grant=grant1,
                                  role=pm_role, user=pm)

        # NOTE: unable to test cdh staff start/end dates
        # because creating profile fails: won't accept is_staff
        # parameter, but claims there is no default for it
        # # cdh staff member who joined after the grant started
        # cdher1 = User.objects.create(username='cdher1')
        # # cdher1_profile = Profile.objects.create(
        # cdher1_profile = Profile(
        #     user=cdher1, site_id=1, is_staff=True)
        # cdher1_profile.save()
        # dev_title = Title.objects.create(title='Developer')
        # Position.objects.create(
        #     title=dev_title, user=cdher1,
        #     start_date=date(2017, 1, 15))
        # dev_role = Role.objects.create(title='Developer')
        # # add to the first grant with an override of current
        # Membership.objects.create(
        #     project=project, grant=grant1, role=dev_role, user=cdher1,
        #     override_status='current')

    @skip("fixme")
    def test_calculated_membership_dates(self):

        # get current versions of the model
        Membership = self.apps.get_model('projects', 'Membership')

        # pi should only have one membership now
        pi_memberships = Membership.objects.filter(user__username='pi')
        assert pi_memberships.count() == 1
        pi_membership = pi_memberships.first()
        # dates should be based on the combination of grants
        assert pi_membership.start_date == date(2016, 9, 1)
        assert pi_membership.end_date == date(2018, 8, 30)

        # pm should have dates from membership
        pm_membership = Membership.objects.get(user__username='pm')
        assert pm_membership.start_date == date(2016, 9, 1)
        assert pm_membership.end_date == date(2017, 8, 30)

        # cdher who joined part-way should have position start for membership
        # cdh1_membership = Membership.objects.get(user__username='cdher1')
        # assert cdh1_membership.start_date == date(2017, 1, 15)
        # # override of current should result in no end date
        # assert cdh1_membership.end_date is None
