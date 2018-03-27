from random import shuffle

from django.views.generic.base import View, TemplateView
from django.utils.cache import get_conditional_response

from cdhweb.blog.models import BlogPost

from cdhweb.events.models import Event

from cdhweb.projects.models import Project


class LastModifiedMixin(View):

    def last_modified(self):
        # for single-object displayable
        return self.get_object().updated

    def dispatch(self, request, *args, **kwargs):
        response = super(LastModifiedMixin, self).dispatch(request, *args, **kwargs)
        # NOTE: remove microseconds so that comparison will pass,
        # since microseconds are not included in the last-modified header

        last_modified = self.last_modified()
        if last_modified:
            last_modified = self.last_modified().replace(microsecond=0)
            response['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
            last_modified = last_modified.timestamp()

        return get_conditional_response(request,
            last_modified=last_modified, response=response)


class LastModifiedListMixin(LastModifiedMixin):

    def last_modified(self):
        # for list object displayable
        # NOTE: this will error if there are no published items
        queryset = self.get_queryset()
        if queryset.exists():
            return queryset.order_by('updated').first().updated


class Homepage(TemplateView):
    '''Site home page.'''
    template_name = 'site_index.html'

    def get_context_data(self, *args, **kwargs):
        # use up to 6 featured posts if there are any
        updates = BlogPost.objects.featured().recent()[:6]
        if not updates.exists():
            # otherwise use 3 most recent posts
            updates = BlogPost.objects.recent()[:3]

        # get highlighted, published projects
        # TODO: (maybe) published(for_user=request.user)
        projects = list(Project.objects.published().highlighted())
        # randomize the project list
        shuffle(projects)

        # find the next three upcoming, published events
        # TODO: (maybe) published(for_user=request.user) \
        upcoming_events = Event.objects.published().upcoming()[:3]

        return {
            'updates': updates,
            'projects': projects[:4],   # first four of random list
            'events': upcoming_events
        }
