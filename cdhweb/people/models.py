from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.text import slugify
from mezzanine.core.fields import RichTextField, FileField
from mezzanine.core.models import Displayable, CONTENT_STATUS_PUBLISHED, \
    CONTENT_STATUS_DRAFT
from mezzanine.utils.models import AdminThumbMixin, upload_to
from taggit.managers import TaggableManager

from cdhweb.resources.models import Attachment, PublishedQuerySetMixin


class Title(models.Model):
    '''Job titles for people'''
    title = models.CharField(max_length=255, unique=True)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
        null=False)
    # NOTE: defining relationship here because we can't add it to User
    # directly
    positions = models.ManyToManyField(User, through='Position',
        related_name='titles')

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title

    def num_people(self):
        '''Number of people with this position title'''
        # NOTE: maybe more meaningful if count restrict to _current_ titles?
        return self.positions.distinct().count()
    num_people.short_description = '# People'


class Person(User):
    # NOTE: using a proxy model for User so we can customize the
    # admin interface in one place without having to extend the django
    # default user model.
    class Meta:
        proxy = True
        verbose_name_plural = 'People'

    @property
    def current_title(self):
        current_positions = self.positions.filter(end_date__isnull=True)
        if current_positions.exists():
            return current_positions.first().title

    def cdh_staff(self):
        '''is CDH staff'''
        try:
            return self.profile.is_staff
        except ObjectDoesNotExist:
            return False
    cdh_staff.boolean = True
    cdh_staff.short_description = 'CDH Staff'

    def published(self):
        '''person has a published profile page'''
        try:
            return self.profile.published()
        except ObjectDoesNotExist:
            return False
    published.boolean = True

    def get_absolute_url(self):
        ''''Display url for user profile'''
        try:
            return self.profile.get_absolute_url()
        except ObjectDoesNotExist:
            pass

    def __str__(self):
        '''Custom person display to make it easier to choose people
        in admin menus.  Uses profile title if available, otherwise combines
        first and last names.  Returns username as last resort if no
        names are set.'''
        try:
            return self.profile.title
        except ObjectDoesNotExist:
            if self.first_name or self.last_name:
                return ' '.join([self.first_name, self.last_name]).strip()
            return self.username


class ProfileQuerySet(PublishedQuerySetMixin):

    def staff(self):
        '''Return only CDH staff members'''
        return self.filter(is_staff=True)

    def _current_position_query(self):
        return (models.Q(user__positions__end_date__isnull=True) |
                models.Q(user__positions__end_date__gte=date.today()))

    def current(self):
        '''Return profiles for users with a current position, either
        with no end date set or an end date in the future.'''
        return self.filter(self._current_position_query())

    def not_current(self):
        '''Return profiles for users without a current position, based on
        no end date set or an end date in the future.'''
        return self.exclude(self._current_position_query())

    def order_by_position(self):
        '''order by job title sort order and then by start date'''
        # annotate to avoid duplicates in the queryset due to multiple positions
        # sort on highest position title and earliest start date (may
        # not be from the same position)
        return self.annotate(max_title=models.Max('user__positions__title__sort_order'),
                             min_start=models.Min('user__positions__start_date')) \
                   .order_by('max_title', 'min_start')


class Profile(Displayable, AdminThumbMixin):
    user = models.OneToOneField(User)
    is_staff = models.BooleanField(default=False,
        help_text='If checked, this person will be listed on the CDH staff page.')
    education = RichTextField()
    bio = RichTextField()
    # NOTE: could use regex here, but how standard are staff phone
    # numbers? or django-phonenumber-field, but that's probably overkill
    phone_number = models.CharField(max_length=50, blank=True)
    office_location = models.CharField(max_length=255, blank=True)

    image = FileField(verbose_name="Image",
        upload_to=upload_to("people.image", "people"),
        format="Image", max_length=255, null=True, blank=True)

    thumb = FileField(verbose_name="Thumbnail",
        upload_to=upload_to("people.image", "people/thumbnails"),
        format="Image", max_length=255, null=True, blank=True)

    admin_thumb_field = "thumb"

    attachments = models.ManyToManyField(Attachment, blank=True)

    tags = TaggableManager(blank=True)

    # custom manager for additional queryset filters
    objects = ProfileQuerySet.as_manager()

    def __str__(self):
        # FIXME: should this be self.title instead?
        return ' '.join([self.user.first_name, self.user.last_name])

    def get_absolute_url(self):
        return reverse('people:profile', kwargs={'slug': self.slug})

    @property
    def current_title(self):
        # FIXME: dowe actually need this here?
        return self.user.current_title


def workshops_taught(user):
    '''Return a QuerySet for the list of workshop events taught by a
    particular user.'''
    return user.event_set.filter(event_type__name='Workshop')

# patch in to user for convenience  (may want to change)
User.workshops_taught = workshops_taught


class Position(models.Model):
    '''Through model for many-to-many relation between people
    and titles.  Adds start and end dates to the join table.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name='positions')
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return '%s %s (%s)' % (self.user, self.title, self.start_date.year)

    @property
    def is_current(self):
        '''is position current - start date before today and end date
        in the future or not set'''
        today = date.today()
        return self.start_date <= today and \
            (not self.end_date or self.end_date > today)

    @property
    def years(self):
        '''year or year range for display'''
        val = str(self.start_date.year)

        if self.end_date:
            # start and end the same year - return single year only
            if self.start_date.year == self.end_date.year:
                return val

            return '%s–%s' % (val, self.end_date.year)

        return '%s–' % val


def init_profile_from_ldap(user, ldapinfo):
    '''Extra user/profile init logic for auto-populating people
    profile fields with data available in LDAP.'''

    user.email = user.email.lower()
    user.save()

    try:
        profile = user.profile
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=user)

    # populate profile with data we can pull from ldap
    # - set user's display name as page title
    profile.title = str(ldapinfo.displayName)
    # - generate a slug based on display name
    profile.slug = slugify(ldapinfo.displayName)
    if ldapinfo.telephoneNumber:
        profile.phone_number = str(ldapinfo.telephoneNumber)
    # 'street' in ldap is office location
    if ldapinfo.street:
        profile.office_location = str(ldapinfo.street)

    # set profiles to draft by default so we don't get a new page
    # for every account we initialize
    profile.status = CONTENT_STATUS_DRAFT
    profile.save()

    # NOTE: job title is available in LDAP; attaching to a person
    # currently requires at least a start date (which is not available
    # in LDAP), but we can at least ensure the title is defined
    # so it can easily be associated with the person

    # only do if the person has a title set
    if ldapinfo.title:
        # job title in ldap is currently stored as
        # job title, organizational unit
        job_title = str(ldapinfo.title).split(',')[0]
        Title.objects.get_or_create(title=job_title)

