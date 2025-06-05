import datetime

import icalendar
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView
from django.views.generic.detail import DetailView

from cdhweb.events.models import Event, EventsLandingPage
from cdhweb.pages.views import LastModifiedListMixin, LastModifiedMixin


class EventMixinView:
    """View mixin that sets model to Event and returns a
    published Event queryset."""

    model = Event
    lastmodified_attr = "last_published_at"

    def get_queryset(self):
        """use manager to find published events only"""
        return Event.objects.live()


class EventSemesterDates:
    """Mixin to return list of event semester dates based on
    event dates in the system."""

    @staticmethod
    def get_semester(date):
        """Return the semester a date occurs in as a string."""
        # determine semester based on the month
        if date.month <= 5:
            return "Spring"
        if date.month <= 8:
            return "Summer"
        return "Fall"

    def get_semester_date_list(self):
        """Get a list of semester labels (semester and year) for published
        events. Semesters are Spring (through May), Summer (through
        August), and Fall."""
        date_list = []
        dates = Event.objects.live().dates("start_time", "month", order="ASC")
        for date in dates:
            # add semester + year to list if not already present
            sem_date = (self.get_semester(date), date.year)
            if sem_date not in date_list:
                date_list.append(sem_date)

        return date_list


class EventsLandingPageView(TemplateView, EventSemesterDates):
    model = EventsLandingPage
    template_name = "events/events_landing_page.html"
    context_object_name = "events_landing_page"

    def get_object(self):
        return EventsLandingPage.objects.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        semester = self.kwargs.get("semester")
        year = self.kwargs.get("year")

        if semester and year:
            upcoming_events = self.get_object().get_events_for_semester(
                semester, int(year)
            )
            context["events"] = upcoming_events
        else:
            # if semester and year are not supplied then supply the upcoming events
            upcoming_events = self.get_object().get_upcoming_events()
            context["events"] = upcoming_events

        context["date_list"] = self.get_semester_date_list()
        context["self"] = self.get_object()

        return context


class UpcomingEventsView(EventMixinView, EventSemesterDates, LastModifiedListMixin):
    """Upcoming events view.  Displays future published events and
    6 most recent past events."""

    date_field = "start_time"
    allow_future = True
    context_object_name = "events"
    allow_empty = True  # don't 404 even if no events in the system
    template_name = "cdhpages/events/events_landing_page.html"

    # NOTE: can't use get_queryset to restrict to upcoming because
    # that affects the archive date list as well; restricting to upcoming
    # events in get_context_data instaed
    def get_context_data(self, *args, **kwargs):
        context = super(UpcomingEventsView, self).get_context_data(*args, **kwargs)

        # Fetch child pages of the EventsLandingPage
        child_pages = EventsLandingPage.get_children().live()

        # Fetch upcoming events among the child pages
        current_datetime = timezone.now()
        upcoming_events = child_pages.filter(
            event__start_time__gte=current_datetime
        ).order_by("event__start_time")

        context["upcoming_events"] = upcoming_events
        event_qs = context["events"]
        context.update(
            {
                "events": event_qs.upcoming(),
                "page_title": "Upcoming Events",
                # find 6 most recent past events
                "past": event_qs.recent()[:6],
                "date_list": self.get_semester_date_list(),
            }
        )
        return context

    def last_modified(self):
        """Get the recent last modified date from included events."""
        upcoming = self.get_queryset().upcoming()
        # don't error if there are no upcoming events
        if upcoming.exists():
            return getattr(
                upcoming.order_by(self.lastmodified_attr).first(),
                self.lastmodified_attr,
            )


class EventSemesterArchiveView(
    EventMixinView, YearArchiveView, EventSemesterDates, LastModifiedListMixin
):
    """Display events by semester"""

    date_field = "start_time"
    make_object_list = True
    allow_future = True
    template_name = "cdhpages/events/events_landing_page.html"
    context_object_name = "events"
    date_list_period = "month"

    # use month/year archive on the blog and then collapse
    semester_dates = {
        # spring: jan 1 - may 31
        "spring": {"start": (1, 1), "end": (5, 31)},
        # summer: june 1 - aug 31
        "summer": {"start": (6, 1), "end": (8, 31)},
        # fall: sep 1 -  dec 31
        "fall": {"start": (9, 1), "end": (12, 31)},
    }

    def get_queryset(self):
        return super().get_queryset().prefetch_related("page_ptr")

    def get_dated_items(self):
        date_list, items, context = super(
            EventSemesterArchiveView, self
        ).get_dated_items()

        # year archive gets items by years; filter by semester
        semester = self.kwargs["semester"]
        # generate dates for start and end with current year
        month, year = self.semester_dates[semester]["start"]
        start = datetime.datetime(
            int(self.kwargs["year"]),
            month,
            year,
            tzinfo=timezone.get_default_timezone(),
        )
        month, year = self.semester_dates[semester]["end"]
        end = datetime.datetime(
            int(self.kwargs["year"]),
            month,
            year,
            tzinfo=timezone.get_default_timezone(),
        )
        items = items.filter(
            start_time__gte=start, start_time__lte=end
        ).order_by_start()

        return (date_list, items, context)

    def get_date_list(self, *args, **kwargs):
        return self.get_semester_date_list()

    def get_context_data(self, *args, **kwargs):
        context = super(EventSemesterArchiveView, self).get_context_data(
            *args, **kwargs
        )
        context.update(
            {
                "page_title": "%s %s Events"
                % (self.kwargs["semester"].title(), self.kwargs["year"])
            }
        )
        return context


class EventDetailView(EventMixinView, DetailView, LastModifiedMixin):
    """Event detail page"""

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset().live()
        queryset = queryset.filter(
            slug=self.kwargs["slug"],
            start_time__year=self.kwargs["year"],
            start_time__month=self.kwargs["month"],
        )
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No Event found found matching the query")
        return obj

    def get(self, request, *args, **kwargs):
        """Serve the requested Event using Wagtail's `Page.serve()`."""
        return self.get_object().serve(request)


class EventIcalView(EventDetailView):
    """Download event information as ical"""

    def get(self, request, *args, **kwargs):
        event = self.get_object()
        cal = icalendar.Calendar()
        cal.add_component(event.ical_event())
        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response["Content-Disposition"] = 'attachment; filename="%s.ics"' % event.slug
        return response


# ical calendar for all upcoming events
# TODO when we can get to it
# class IcalCalendarView(EventListView):

#     def get_queryset(self):
#         return super(IcalCalendarView, self).get_queryset().upcoming()

#     def render_to_response(self, context, **response_kwargs):
#         cal = icalendar.Calendar()
#         # TODO: required to be compliant
#         # cal.add('prodid', '-//My calendar product//mxm.dk//')
#         # cal.add('version', '2.0')
#         for event in self.get_queryset():
#             cal.add_component(event.ical_event())
#         # TODO: should support cancelled events if possible
#         response = HttpResponse(cal.to_ical(), content_type="text/calendar")
#         response['Content-Disposition'] = 'attachment; filename="CDH-calendar.ics"'
#         return response
