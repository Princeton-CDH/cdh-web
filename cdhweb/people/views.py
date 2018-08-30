from datetime import date

from django.conf import settings
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

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

    def get_queryset(self):
        # only published profiles with staff flag get a detail page
        return super().get_queryset().staff()

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


class ProfileListView(ProfileMixinView, ListView, LastModifiedListMixin):
    '''Base class for profile list views'''

    #: title for this category of people
    page_title = ''
    #: title for non-past people in this category of people
    current_title = ''
    #: label for past people in this category of people
    past_title = ''

    def get_queryset(self):
        # get published profile ordered by position (job title then start date)
        return super().get_queryset().order_by_position().distinct()

    def get_context_data(self):
        context = super().get_context_data()
        # update context to display current and past people separately
        current = self.object_list.current()
        # filter past based current ids, rather than trying to do the complicated
        # query to find not current people
        past = self.object_list.exclude(id__in=current.values('id'))
        context.update({
            'current': current,
            'past': past,
            'title': self.page_title,
            'past_title': self.past_title,
            'current_title': self.current_title or self.page_title, # use main title as default
            'archive_nav_urls': [
                ('Staff', reverse('people:staff')),
                ('Postdoctoral Fellows', reverse('people:postdocs')),
                ('Students', reverse('people:students')),
                ('Speakers', reverse('people:speakers')),
            ]
        })
        return context


class StaffListView(ProfileListView):
    '''Display current and past CDH staff'''
    page_title = 'Staff'
    past_title = 'Staff Alumni'

    def get_queryset(self):
        # filter to profiles with staff flag set and exclude postdocs
        # and students
        # (already ordered by job title sort order and then by last name)
        return super().get_queryset().staff().not_postdocs().not_students()
        # NOTE: this won't filter correctly if we ever have someone who
        # goes from a postdoc or student role to a staff position, however
        # filtering only on current role messes up staff alumni

class PostdocListView(ProfileListView):
    '''Display current and past postdoctoral fellows'''
    page_title = 'Postdoctoral Fellows'
    past_title = 'Postoctoral Fellow Alumni'

    def get_queryset(self):
        # filter to just postdocs
        return super().get_queryset().postdocs()


class StudentListView(ProfileListView):
    '''Display current and past graduate fellows, graduate and undergraduate
    assistants.'''
    page_title = 'Students'
    past_title = 'Student Alumni'

    def get_queryset(self):
        # filter to just students
        return super().get_queryset().students()

class SpeakerListView(ProfileListView):
    '''Display upcoming and past speakers.'''
    page_title = 'Speakers'
    current_title = 'Upcoming Speakers' # set a special title for "current"
    past_title = 'Past Speakers'

    def get_queryset(self):
        return Profile.objects.speakers()

    def get_context_data(self):
        context = super().get_context_data()
        # use distinct() to get around duplication caused by many-many relationship with events
        current = self.object_list.current().distinct()
        past = self.object_list.exclude(id__in=current.values('id'))

        context.update({
            'current': current,
            'past': past,
            'show_events': True # show upcoming and past events associated with the speakers
        })
        return context
