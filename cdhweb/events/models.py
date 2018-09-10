# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
import icalendar

from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, RichText
from mezzanine.utils.models import AdminThumbMixin, upload_to
from taggit.managers import TaggableManager

from cdhweb.people.models import Person
from cdhweb.resources.models import Attachment, ExcerptMixin, PublishedQuerySetMixin
from cdhweb.resources.utils import absolutize_url


class EventTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class EventType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    objects = EventTypeManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name, )


class Location(models.Model):
    name = models.CharField(max_length=255,
        help_text='Name of the location')
    short_name = models.CharField(max_length=80, blank=True)
    address = models.CharField(max_length=255,
        help_text='Addres of the location (will not display if same as name)')

    def __str__(self):
        return self.short_name or self.name

    @property
    def display_name(self):
        if self.name and self.address and self.name != self.address:
            return ', '.join([self.name, self.address])
        return self.name


class EventQuerySet(PublishedQuerySetMixin):

    def upcoming(self):
        '''Find upcoming events. Includes events that end on the current
        day even if the start time is past.'''
        now = timezone.now()
        # construct a datetime based on now but with zero hour/minute/second
        today = datetime(now.year, now.month, now.day,
            tzinfo=timezone.get_default_timezone())
        return self.filter(end_time__gte=today)

    def recent(self):
        '''Find past events, most recent first.  Only includes events
        with end date in the past.'''
        now = timezone.now()
        # construct a datetime based on now but with zero hour/minute/second
        today = datetime(now.year, now.month, now.day,
            tzinfo=timezone.get_default_timezone())
        return self.filter(end_time__lt=today).order_by('-start_time')


class Event(Displayable, RichText, AdminThumbMixin, ExcerptMixin):
    '''An event, such as a workshop, lecture, or conference.'''

    # description = rich text field
    # NOTE: do we want a sponsor field? or jest include in description?
    sponsor = models.CharField(max_length=80, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # all day flag todo
    # all_day = models.BooleanField(default=False, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
    event_type = models.ForeignKey(EventType)
    speakers = models.ManyToManyField(Person,
        help_text='Guest lecturer(s) or Workshop leader(s)',
        blank=True)

    attendance = models.PositiveIntegerField(null=True, blank=True,
        help_text='Total number of people who attended the event. (Internal only, for reporting purposes.)')

    # TODO: include expected size? (required size?)
    image = FileField(verbose_name="Image",
        upload_to=upload_to("events.image", "events"),
        format="Image", max_length=255, null=True, blank=True,
        help_text='Image for display on event detail page (optional)')

    thumb = FileField(verbose_name="Thumbnail",
        upload_to=upload_to("events.thumb", "events/thumbnails"),
        format="Image", max_length=255, null=True, blank=True,
        help_text='Image for display on event card (optional)')

    attachments = models.ManyToManyField(Attachment, blank=True)

    tags = TaggableManager(blank=True)

    # override manager for custom queryset filters
    objects = EventQuerySet.as_manager()

    admin_thumb_field = "thumb"
    event_type.verbose_name = 'Type'

    def __str__(self):
        return ' - '.join([self.title, self.start_time.strftime('%b %d, %Y')])

    class Meta:
        ordering = ("start_time",)

    def get_absolute_url(self):
        '''event detail url on this site'''
        # we don't have to worry about the various url config options
        # that mezzanine has to support; just handle the url style we
        # want to use locally
        return reverse('event:detail', kwargs={
            'year': self.start_time.year,
            # force two-digit month
            'month': '%02d' % self.start_time.month,
            'slug': self.slug})


    def full_url(self):
        '''Absolute url, including site address'''
        return absolutize_url(self.get_absolute_url())

    def get_ical_url(self):
        '''URL to download this event as ical'''
        return reverse('event:ical', kwargs={
            'year': self.start_time.year,
            # force two-digit month
            'month': '%02d' % self.start_time.month,
            'slug': self.slug})

    def when(self):
        '''Event start/end date and time, formatted for display.
        Removes leading zeros from hours and converts am/pm to lower case.'''

        # NOTE: - in %-I is to remove leading zero
        # (possibly platform specific?)

        local_tz = timezone.get_default_timezone()
        # convert dates to local timezone for display
        local_start = self.start_time.astimezone(local_tz)
        local_end = self.end_time.astimezone(local_tz)
        start = ' '.join([local_start.strftime('%b %d'),
                          local_start.strftime('%-I:%M')])
        start_ampm = local_start.strftime('%p')
        # include start am/pm if *different* from end
        if start_ampm != local_end.strftime('%p'):
            start += ' %s' % start_ampm.lower()

        # include end month and day if *different* from start
        end_pieces = []
        if local_start.month != local_end.month:
            end_pieces.append(local_end.strftime('%b %d'))
        elif local_start.day != local_end.day:
            end_pieces.append(local_end.strftime('%d'))
        end_pieces.append(local_end.strftime('%-I:%M %p').lower())
        end = ' '.join(end_pieces)

        return ' – '.join([start, end])

    def duration(self):
        '''duration between start and end time as :class:`datetime.timedelta`'''
        return self.end_time - self.start_time

    def ical_event(self):
        '''Return the current event as a :class:`icalendar.Event` for
        inclusion in a :class:`icalendar.Calendar`'''
        event = icalendar.Event()
        # use absolute url for event id and in event content
        absurl = self.full_url()
        event.add('uid', absurl)
        event.add('summary', self.title)
        event.add('dtstart', self.start_time)
        event.add('dtend', self.end_time)
        if self.location:
            event.add('location', self.location.display_name)
        event.add('description',
            '\n'.join([strip_tags(self.content), '', absurl]))
        return event

