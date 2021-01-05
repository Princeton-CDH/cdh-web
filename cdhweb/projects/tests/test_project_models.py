from unittest import skip
from datetime import date, datetime, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.html import escape
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)

from cdhweb.people.models import Profile
from cdhweb.projects.models import (Grant, GrantType, Membership, Project,
                                    ProjectResource, Role)
from cdhweb.projects.sitemaps import ProjectSitemap
from cdhweb.resources.models import ResourceType


class TestGrantType(TestCase):

    def test_str(self):
        grtype = GrantType(grant_type='Sponsored Project')
        assert str(grtype) == grtype.grant_type


class TestRole(TestCase):

    def test_str(self):
        role = Role(title='Principal Investigator')
        assert str(role) == role.title


@skip("fixme")
class TestProject(TestCase):
    fixtures = ['test_project_data.json']

    def setUp(self):
        # project
        self.project = Project.objects.get(title="Derrida's Margins")
        # grants
        self.grant1 = Grant.objects.get(
            end_date=date(year=2016, month=1, day=1))
        self.grant2 = Grant.objects.get(
            end_date=date(year=2017, month=1, day=1))
        # users
        self.katie = get_user_model().objects.get(username='katie')
        self.koeser = get_user_model().objects.get(username='koeser')
        self.munson = get_user_model().objects.get(username='munson')
        self.chloe = get_user_model().objects.get(username='vettier')

    def test_str(self):
        assert str(self.project) == self.project.title

    def test_get_absolute_url(self):
        resolved_url = resolve(self.project.get_absolute_url())
        assert resolved_url.namespace == 'project'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['slug'] == self.project.slug

    def test_website_url(self):
        # no website resource url
        assert self.project.website_url is None
        # add a website url
        website = ResourceType.objects.get(name='Website')
        derrida_url = 'http://derridas-margins.princeton.edu'
        ProjectResource.objects.create(project=self.project, resource_type=website,
                                       url=derrida_url)
        assert self.project.website_url == derrida_url

    def test_latest_grant(self):
        assert self.project.latest_grant() == self.grant2

    def test_current_memberships(self):
        # if all grants are ended,
        # should get memberships from most recent grant
        current_members = [m.person for m in self.project.current_memberships()]
        assert self.katie in current_members        # katie is director on both grants
        assert self.chloe in current_members        # chloe is on this grant only
        assert self.munson not in current_members   # rm was on older grant only
        assert self.koeser not in current_members   # rsk was on older grant only
        # memberships with end date included in last grant period should be included
        today = timezone.now().date()
        m = Membership.objects.get(person=self.munson)
        m.end_date = today
        m.save()
        current_members = [m.person for m in self.project.current_memberships()]
        assert self.katie in current_members        # unchanged
        assert self.chloe in current_members        # unchanged
        assert self.munson in current_members       # now forced current
        assert self.koeser not in current_members   # unchanged
        # memberships with end date before last grant should not be included
        m = Membership.objects.get(person=self.chloe)
        m.end_date = date(2015, 9, 2)
        m.save()
        current_members = [m.person for m in self.project.current_memberships()]
        assert self.katie in current_members        # unchanged
        assert self.chloe not in current_members    # forced past
        assert self.munson in current_members       # forced current
        assert self.koeser not in current_members   # unchanged

    def test_alums(self):
        # should get members from older grant (2015-2016) by default
        alums = self.project.alums()
        assert self.katie not in alums      # not an alum since on both grants
        assert self.chloe not in alums  # chloe is on newer grant only
        assert self.munson in alums     # rm is on this grant
        assert self.koeser in alums     # rsk is on this grant
        # memberships with end date before most recent grant should be included
        m = Membership.objects.get(person=self.chloe)
        m.end_date = date(2015, 9, 2)
        m.save()
        alums = self.project.alums()
        assert self.katie not in alums   # unchanged
        assert self.chloe in alums   # now past by date
        assert self.munson in alums  # unchanged
        assert self.koeser in alums  # unchanged
        # memberships with end date unset
        m = Membership.objects.get(person=self.koeser)
        m.end_date = None
        m.save()
        alums = self.project.alums()
        assert self.katie not in alums   # unchanged
        assert self.chloe in alums       # forced past
        assert self.munson in alums      # unchanged
        assert self.koeser not in alums  # forced current


class TestProjectQuerySet(TestCase):

    def test_highlighted(self):
        proj = Project.objects.create(title="Derrida's Margins")

        assert not Project.objects.highlighted().exists()

        proj.highlight = True
        proj.save()
        assert Project.objects.highlighted().exists()

    def test_current(self):
        today = datetime.today()
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # asocciated grant has ended
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=today - timedelta(days=2),
                                     end_date=today - timedelta(days=1))

        assert not Project.objects.current().exists()

        # grant ends in the future
        grant.end_date = today + timedelta(days=1)
        grant.save()
        assert Project.objects.current().exists()

        # grant end date is not set
        grant.end_date = None
        grant.save()
        assert Project.objects.current().exists()

    def test_not_current(self):
        today = datetime.today()
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # asocciated grant has ended
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=today - timedelta(days=2),
                                     end_date=today - timedelta(days=1))

        assert Project.objects.not_current().exists()

        # grant end date in the future
        grant.end_date = today + timedelta(days=1)
        grant.save()
        assert not Project.objects.not_current().exists()

        # grant end date is not set
        grant.end_date = None
        grant.save()
        assert not Project.objects.not_current().exists()

    def test_staff_or_postdoc(self):
        # create staff, postdoc, and other project
        start = datetime.today() - timedelta(days=30)
        staff_proj = Project.objects.create(title="Pliny Project")
        staff_rd = GrantType.objects.get_or_create(grant_type='Staff R&D')[0]
        Grant.objects.create(project=staff_proj, grant_type=staff_rd,
                             start_date=start)
        postdoc_proj = Project.objects.create(
            title="Linked Global Networks of Cultural Production")
        postdoc_grant = GrantType.objects.get_or_create(
            grant_type='Postdoctoral Research Project')[0]
        Grant.objects.create(project=postdoc_proj, grant_type=postdoc_grant,
                             start_date=start)
        other_proj = Project.objects.create(title="Derrida's Margins")

        staff_postdoc_projects = Project.objects.staff_or_postdoc()
        assert staff_proj in staff_postdoc_projects
        assert postdoc_proj in staff_postdoc_projects
        assert other_proj not in staff_postdoc_projects

    def test_not_staff_or_postdoc(self):
        # create staff, postdoc, and other project
        start = datetime.today() - timedelta(days=30)
        staff_proj = Project.objects.create(title="Pliny Project")
        staff_rd = GrantType.objects.get_or_create(grant_type='Staff R&D')[0]
        Grant.objects.create(project=staff_proj, grant_type=staff_rd,
                             start_date=start)
        postdoc_proj = Project.objects.create(
            title="Linked Global Networks of Cultural Production")
        postdoc_grant = GrantType.objects.get_or_create(
            grant_type='Postdoctoral Research Project')[0]
        Grant.objects.create(project=postdoc_proj, grant_type=postdoc_grant,
                             start_date=start)
        other_proj = Project.objects.create(title="Derrida's Margins")

        non_staff_postdoc_projects = Project.objects.not_staff_or_postdoc()
        assert staff_proj not in non_staff_postdoc_projects
        assert postdoc_proj not in non_staff_postdoc_projects
        assert other_proj in non_staff_postdoc_projects

    def test_order_by_newest_grant(self):
        # create three test projects with grants in successive years
        sponsored = GrantType.objects.get_or_create(
            grant_type='Sponsored Project')[0]
        p1 = Project.objects.create(title="One")
        Grant.objects.create(project=p1, grant_type=sponsored,
                             start_date=date(2015, 9, 1))
        p2 = Project.objects.create(title="Two")
        Grant.objects.create(project=p2, grant_type=sponsored,
                             start_date=date(2016, 9, 1))
        p3 = Project.objects.create(title="Three")
        Grant.objects.create(project=p3, grant_type=sponsored,
                             start_date=date(2017, 9, 1))

        ordered = Project.objects.order_by_newest_grant()
        # should be ordered newest first
        assert ordered[0] == p3
        assert ordered[1] == p2
        assert ordered[2] == p1

        # with multiple grants, still orders based on newest grant
        Grant.objects.create(project=p3, grant_type=sponsored,
                             start_date=date(2015, 9, 1))

        ordered = Project.objects.order_by_newest_grant()
        # should be ordered newest first
        assert ordered[0] == p3

    def test_published(self):
        # technically a mixin method, testing here for convenience

        staffer = get_user_model().objects.create(username='staffer',
                                                  is_staff=True)
        nonstaffer = get_user_model().objects.create(username='nonstaffer',
                                                     is_staff=False)

        # careate project in draft status
        proj = Project.objects.create(title="Derrida's Margins",
                                      status=CONTENT_STATUS_DRAFT)

        # draft displayable only listed for staff user
        assert proj not in Project.objects.published()
        assert proj not in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # set to published, no dates
        proj.status = CONTENT_STATUS_PUBLISHED
        proj.save()

        # published displayable listed for everyone
        assert proj in Project.objects.published()
        assert proj in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # publish date in future - only visible to staff user
        proj.publish_date = timezone.now() + timedelta(days=2)
        proj.save()
        assert proj not in Project.objects.published()
        assert proj not in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # publish date in past - visible to all
        proj.publish_date = timezone.now() - timedelta(days=2)
        proj.save()
        assert proj in Project.objects.published()
        assert proj in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # expiration date in past - only visible to staff user
        proj.expiry_date = timezone.now() - timedelta(days=2)
        proj.save()
        assert proj not in Project.objects.published()
        assert proj not in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

    def test_working_groups(self):
        wg = Project.objects.create(
            title="My DH Working Group", working_group=True)
        derrida = Project.objects.get_or_create(title="Derrida's Margins")

        # should include only working groups
        all_wgs = Project.objects.working_groups()
        assert wg in all_wgs
        assert derrida not in all_wgs


class TestGrant(TestCase):

    def test_str(self):
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        start_year, end_year = (2016, 2017)
        grant = Grant(project=proj, grant_type=grtype,
                      start_date=datetime(start_year, 1, 1),
                      end_date=datetime(end_year, 1, 1))
        assert str(grant) == '%s: %s (2016–2017)' % \
            (proj.title, grtype.grant_type)


class TestMembership(TestCase):

    @skip("fixme")
    def test_str(self):
        # create test objects needed for a membership
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=datetime(2016, 1, 1),
                                     end_date=datetime(2017, 1, 1))
        user = get_user_model().objects.create(username='contributor')
        role = Role.objects.create(title='Data consultant', sort_order=1)
        membership = Membership.objects.create(
            project=proj, person=user, role=role, start_date=grant.start_date)

        assert str(membership) == '%s - %s on %s (%s)' % (user, role, proj,
                                                          membership.years)


class TestProjectResource(TestCase):

    def test_display_url(self):
        base_url = 'derridas-margins.princeton.edu'
        project_url = 'http://%s' % base_url
        proj = Project.objects.create(title="Derrida's Margins")
        website = ResourceType.objects.get(name='Website')
        res = ProjectResource.objects.create(project=proj, resource_type=website,
                                             url=project_url)
        assert res.display_url() == base_url

        # https
        res.url = 'https://%s' % base_url
        assert res.display_url() == base_url


class TestViews(TestCase):

    def test_list(self):
        # create test project
        proj = Project.objects.create(title="Derrida's Margins")
        # add a grant that is current (has not ended)
        today = datetime.today()
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        Grant.objects.create(project=proj, grant_type=grtype,
                             start_date=today - timedelta(days=30),
                             end_date=today + timedelta(days=30))

        response = self.client.get(reverse('project:list'))
        assert proj in response.context['project_list']
        self.assertContains(response, escape(proj.title))
        self.assertContains(response, proj.get_absolute_url())
        self.assertContains(response, proj.short_description)
        # no external link
        self.assertNotContains(
            response, '<a class="external" title="Project Website"')
        # no 'built by cdh' flag
        self.assertNotContains(response, 'Built by CDH')

        # add link, set as built by cdh
        website = ResourceType.objects.get(name='Website')
        project_url = 'http://derridas-margins.princeton.edu'
        ProjectResource.objects.create(project=proj, resource_type=website,
                                       url=project_url)
        proj.cdh_built = True
        proj.save()
        response = self.client.get(reverse('project:list'))
        self.assertContains(
            response, '<a class="external" title="Project Website"')
        self.assertContains(response, project_url)
        self.assertContains(response, 'Built by CDH')

        # check past projects
        proj = Project.objects.create(title="Derrida's Margins")
        response = self.client.get(reverse('project:list'))
        assert proj not in response.context['project_list']
        assert proj in response.context['past_projects']

        # TODO: test thumbnail image?

    def test_staff_list(self):
        # create staff, postdoc, and other project
        start = datetime.today() - timedelta(days=30)
        staff_proj = Project.objects.create(title="Pliny Project")
        staff_rd = GrantType.objects.get_or_create(grant_type='Staff R&D')[0]
        Grant.objects.create(project=staff_proj, grant_type=staff_rd,
                             start_date=start)
        postdoc_proj = Project.objects.create(
            title="Linked Global Networks of Cultural Production")
        postdoc_grant = GrantType.objects.get_or_create(
            grant_type='Postdoctoral Research Project')[0]
        Grant.objects.create(project=postdoc_proj, grant_type=postdoc_grant,
                             start_date=start)
        other_proj = Project.objects.create(title="Derrida's Margins")

        response = self.client.get(reverse('project:staff'))
        # sponsored project not on staff page
        self.assertNotContains(response, other_proj.get_absolute_url())

        # staff & post-doc projects are displayed
        self.assertContains(response, staff_proj.title)
        self.assertContains(response, staff_proj.get_absolute_url())
        self.assertContains(response, postdoc_proj.title)
        self.assertContains(response, postdoc_proj.get_absolute_url())

        # not testing display specifics since re-used from main project list

    def test_working_group_list(self):
        # create a working group
        wg = Project.objects.create(
            title="My DH Working Group", working_group=True)
        derrida, _ = Project.objects.get_or_create(title="Derrida's Margins")

        response = self.client.get(reverse('project:working-groups'))
        # sponsored project not on working group page
        self.assertNotContains(response, derrida.get_absolute_url())

        # working group is displayed
        self.assertContains(response, wg.title)
        self.assertContains(response, wg.get_absolute_url())

        # working groups page shouldn't have a "past projects" section
        self.assertNotContains(response, "Past Projects")

        # create a grant for the working group that ended in the past
        start = datetime.today() - timedelta(days=120)
        end = datetime.today() - timedelta(days=30)
        seed, _ = GrantType.objects.get_or_create(grant_type='Seed')
        Grant.objects.create(project=wg, grant_type=seed,
                             start_date=start, end_date=end)

        # still shouldn't have a "past projects" section
        self.assertNotContains(response, "Past Projects")

    @skip("fixme")
    def test_detail(self):
        proj = Project.objects.create(title="Derrida's Margins",
                                      slug='derrida', short_description='Citations and interventions',
                                      long_description='<p>an annotation project</p>')
        today = datetime.today()
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=today - timedelta(days=2),
                                     end_date=today + timedelta(days=1))
        # add project members to test contributor display
        contrib1 = get_user_model().objects.create(username='contributor one')
        contrib2 = get_user_model().objects.create(username='contributor two')
        contrib3 = get_user_model().objects.create(username='contributor three')
        site = Site.objects.first()
        Profile.objects.bulk_create([
            Profile(user=contrib1, title=contrib1.username, site=site),
            Profile(user=contrib2, title=contrib2.username, site=site),
            Profile(user=contrib3, title=contrib3.username, site=site)
        ])
        consult = Role.objects.create(title='Consultant', sort_order=2)
        pi = Role.objects.create(title='Principal Investigator', sort_order=1)
        Membership.objects.bulk_create([
            Membership(project=proj, person=contrib1, role=consult, start_date=grant.start_date),
            Membership(project=proj, person=contrib2, role=consult, start_date=grant.start_date),
            Membership(project=proj, person=contrib3, role=pi, start_date=grant.start_date)
        ])
        # add a website url
        website = ResourceType.objects.get(name='Website')
        project_url = 'http://something.princeton.edu'
        ProjectResource.objects.create(project=proj, resource_type=website,
                                       url=project_url)

        response = self.client.get(reverse('project:detail',
                                           kwargs={'slug': proj.slug}))
        assert response.context['project'] == proj
        self.assertContains(response, escape(proj.title))
        self.assertContains(response, proj.short_description)
        self.assertContains(response, proj.long_description)
        # contributors
        self.assertContains(response, consult.title, count=1,
                            msg_prefix='contributor roles should only show up once')
        self.assertContains(response, pi.title, count=1,
                            msg_prefix='contributor roles should only show up once')
        for contributor in [contrib1, contrib2, contrib3]:
            self.assertContains(response, contributor.profile.title)
        self.assertContains(response, project_url)

        # test grant dates displayed
        self.assertContains(response, '<h2>CDH Grant History</h2>')
        self.assertContains(response,
                            '%s %s' % (grant.years, grant.grant_type))

        # if for some reason a project has no grants, should not display grants
        proj.grant_set.all().delete()
        response = self.client.get(reverse('project:detail',
                                           kwargs={'slug': proj.slug}))
        self.assertNotContains(response, '<h2>CDH Grant History</h2>')

        # TODO: test large image included


class TestProjectSitemap(TestCase):

    def test_priority(self):
        proj = Project(title='A project')
        # default
        assert ProjectSitemap().priority(proj) == 0.5
        # cdh built = higher priority
        proj.cdh_built = True
        assert ProjectSitemap().priority(proj) == 0.6
        # simulate website url
        with patch.object(Project, 'website_url', return_val='http://example.com'):
            # cdh built + website = even higher priority
            assert ProjectSitemap().priority(proj) == 0.7

            # website but not cdh built = not quite as high
            proj.cdh_built = False
            assert ProjectSitemap().priority(proj) == 0.6
