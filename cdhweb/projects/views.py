from django.db.models import Count
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from cdhweb.projects.models import Project
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin


class ProjectMixinView(object):
    '''View mixin that sets model to Project and returns a
    published Project queryset.'''
    model = Project
    title = 'Projects'

    def get_queryset(self):
        # use displayable manager to find published events only
        # (or draft profiles for logged in users with permission to view)
        return Project.objects.published() # TODO: published(for_user=self.request.user)


class ProjectListMixinView(ProjectMixinView, ListView, LastModifiedListMixin):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # update context to display current and past projects separately
        context.update({
            'project_list': self.object_list.current(),
            'past_projects': self.object_list.not_current().order_by_newest_grant(),
            'title': self.title
        })
        return context


class ProjectListView(ProjectListMixinView):
    '''Current and past projects, based on grant dates. (Does not include
    staff and postdoc projects.)'''

    def get_queryset(self):
        return super().get_queryset().not_staff_or_postdoc()


class StaffProjectListView(ProjectListMixinView):
    '''Staff projects, based on special staff R&D grant'''

    title = 'Staff and Postdoctoral Fellow Projects'

    def get_queryset(self):
        return super().get_queryset().staff_or_postdoc()


class ProjectDetailView(ProjectMixinView, DetailView, LastModifiedMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context['page'] = self.object
        return context

