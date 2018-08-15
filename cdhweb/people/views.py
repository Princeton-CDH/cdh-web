from datetime import date

from django.conf import settings
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

from cdhweb.people.models import Profile
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin
from cdhweb.resources.utils import absolutize_url


class ProfileMixinView(object):
    '''Profile view mixin that sets model to Profile and returns a
    published Profile queryset.'''

    model = Profile

    def get_queryset(self):
        # use displayable manager to find published profiles only
        # (or draft profiles for logged in users with permission to view)
        return Profile.objects.published() # TODO: published(for_user=self.request.user)



class ProfileDetailView(ProfileMixinView, DetailView, LastModifiedMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context.update({
            'page': self.object,
            'opengraph_type': 'profile'
        })
        if self.object.thumb:
            context['preview_image'] = absolutize_url(''.join([settings.MEDIA_URL,
                str(self.object.thumb)]))

        return context


class ProfileListView(ProfileMixinView, ListView):
    '''Base class for profile list views'''
    page_title = ''
    nav_title = ''

    def get_queryset(self):
        # get published profile ordered by position (job title then start date)
        return super().get_queryset().order_by_position().distinct()

    def get_context_data(self):
        context = super().get_context_data()
        # update context to display current and past people separately
        context.update({
            'current': self.object_list.current(),
            'past': self.object_list.not_current(),
            'title': self.page_title,
            'nav_title': self.nav_title,
            # TODO: generate this from mezzanine menu so it can be re-ordered
            'archive_nav_urls': [
                ('Staff', reverse('people:staff')),
                ('Postdoctoral Fellows', reverse('people:postdocs')),
                ('Students', reverse('people:students')),
            ]
        })
        return context


class StaffListView(ProfileListView):
    '''Display current and past CDH staff'''
    page_title = 'Who we are'
    nav_title = 'Staff'

    def get_queryset(self):
        # filter to profiles with staff flag set
        # order by job title sort order and then by last name
        return super().get_queryset().staff()


class PostdocListView(ProfileListView):
    '''Display current and past postdoctoral fellows'''
    page_title = 'Postdoctoral Fellows'
    nav_title = page_title

    def get_queryset(self):
        # filter to just postdocs
        return super().get_queryset().postdocs()


class StudentListView(ProfileListView):
    '''Display current and past graduate fellows, graduate and undergraduate
    assistants.'''
    page_title = 'Students'
    nav_title = page_title

    def get_queryset(self):
        # filter to just students
        return super().get_queryset().students()

