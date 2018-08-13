from django.db.models import Count
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from cdhweb.projects.models import Project
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin


class ProjectMixinView(object):
    '''View mixin that sets model to Project and returns a
    published Project queryset.'''
    model = Project

    def get_queryset(self):
        # use displayable manager to find published events only
        # (or draft profiles for logged in users with permission to view)
        return Project.objects.published() # TODO: published(for_user=self.request.user)


class ProjectListView(ProjectMixinView, ListView, LastModifiedListMixin):
    pass

    # def get_queryset(self):
        # projects = super().get_queryset()
        # return projects.annotate(has_website=Count(projectresource__resource_type__name='Website'))



class ProjectDetailView(ProjectMixinView, DetailView, LastModifiedMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context['page'] = self.object
        return context

