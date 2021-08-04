from django.utils.cache import get_conditional_response
from django.views.generic import ListView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from wagtail.core.models import Page
from wagtail.search.utils import parse_query_string

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event
from cdhweb.pages.forms import SiteSearchForm
from cdhweb.people.models import Profile
from cdhweb.projects.models import Project


class LastModifiedMixin(View):
    """Mixin that adds last-modified timestamps to response for detail views.

    Uses Django's get_conditional_response to return a 304 if object has not
    been modified since time specified in the HTTP if-modified-since header.
    """

    # override to customize which attribute to use as modification date
    lastmodified_attr = "updated"

    def last_modified(self):
        """Get the last modified date of the view object."""
        return getattr(self.get_object(), self.lastmodified_attr)

    def dispatch(self, request, *args, **kwargs):
        response = super(LastModifiedMixin, self).dispatch(request, *args, **kwargs)

        # NOTE: remove microseconds so that comparison will pass,
        # since microseconds are not included in the last-modified header
        last_modified = self.last_modified()
        if last_modified:
            last_modified = self.last_modified().replace(microsecond=0)
            response["Last-Modified"] = last_modified.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
            last_modified = last_modified.timestamp()

        return get_conditional_response(
            request, last_modified=last_modified, response=response
        )


class LastModifiedListMixin(LastModifiedMixin):
    """Mixin that adds last-modified timestamps to response for list views.

    Uses Django's get_conditional_response to return a 304 if none of the
    objects in the list have been modified since time specified in the HTTP
    if-modified-since header.
    """

    def last_modified(self):
        """Get the most recent modification date among all view objects."""
        queryset = self.get_queryset()
        if queryset.exists():
            return getattr(
                queryset.order_by(self.lastmodified_attr).reverse().first(),
                self.lastmodified_attr,
            )


class SiteSearchView(ListView, FormMixin):
    """Search across all pages on the site."""

    model = Page
    form_class = SiteSearchForm
    paginate_by = 10
    page_title = "Search"
    template_name = "cdhpages/page_search.html"
    filter_models = {
        "everything": Page,
        "people": Profile,
        "updates": BlogPost,
        "projects": Project,
        "events": Event,
    }

    def get_queryset(self):
        # choose the model to search across; Page for everything
        filter = self.request.GET.get("filter", "everything")
        model = self.filter_models[filter]

        # get keyword query; support filters & phrase matching with double quotes
        # see https://docs.wagtail.io/en/stable/topics/search/searching.html#query-string-parsing
        q = self.request.GET.get("q", "")
        _filters, query = parse_query_string(q)

        # execute search against specified model; exclude unpublished pages.
        # results sorted by relevance by default; to override sort the QS first
        # and then pass order_by_relevance=false to .search()
        return model.objects.live().search(query)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # use GET instead of default POST/PUT for form data
        kwargs["data"] = self.request.GET.copy()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"page_title": self.page_title})
        return context
