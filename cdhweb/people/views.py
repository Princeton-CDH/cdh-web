from datetime import date

from django.conf import settings
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from cdhweb.people.models import Profile
from cdhweb.blog.models import BlogPost
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

        # retrieve 3 most recent published blog posts with the current user as author
        recent_posts = BlogPost.objects.filter(users__id=self.object.user.id).published()[:3]

        # also set object as page for common page display functionality
        context.update({
            'page': self.object,
            'opengraph_type': 'profile',
            'recent_posts': recent_posts,
        })
        if self.object.thumb:
            context['preview_image'] = absolutize_url(''.join([settings.MEDIA_URL,
                str(self.object.thumb)]))

        return context


# class ProfileListView(ProfileMixinView, ListView):
#     # NOTE: we probably don't need a full list of all profiles;
#     # instead we'll probably want a few filtered lists, e.g. current
#     # staff, guest speakers, alumni, etc.
#     pass


class StaffListView(ProfileMixinView, ListView, LastModifiedListMixin):

    def get_queryset(self):
        # filter to profiles with staff flag set
        # *and* a current position (no end date or unexpired end date).
        # order by job title sort order and then by last name
        # (TODO: perhaps job start date for secondary sort?)
        return super(StaffListView, self).get_queryset() \
            .staff().current().order_by_position().distinct()

    def get_context_data(self):
        context = super(StaffListView, self).get_context_data()
        context.update({
            'title': 'Who we are',
            'nav_title': 'Who we are | Current',
            'archive_menu_title': 'Current'
        })
        return context


class AlumniListView(ProfileMixinView, ListView, LastModifiedListMixin):

    def get_queryset(self):
        return super(AlumniListView, self).get_queryset() \
            .staff().not_current().order_by_position().distinct()

    def get_context_data(self):
        context = super(AlumniListView, self).get_context_data()
        context.update({
            'title': 'Alumni',
            'nav_title': 'Who we are | Alumni',
            'archive_menu_title': 'Alumni'

        })
        return context



