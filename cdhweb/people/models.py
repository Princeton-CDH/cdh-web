from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.text import slugify
from mezzanine.core.fields import RichTextField, FileField
from mezzanine.core.managers import DisplayableManager
from mezzanine.core.models import Displayable, Slugged
from taggit.managers import TaggableManager


class Title(models.Model):
    '''Job titles for people'''
    title = models.CharField(max_length=255)
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


class Profile(Displayable):
    user = models.OneToOneField(User)
    education = RichTextField()
    bio = RichTextField()
    # NOTE: could use regex here, but how standard are staff phone
    # numbers? or django-phonenumber-field, but that's probably overkill
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    office_location = models.CharField(max_length=255, blank=True, null=True)

    tags = TaggableManager(blank=True)

    # use displayable manager for access to published queryset filter, etc.
    objects = DisplayableManager()

    def __str__(self):
        return ' '.join([self.user.first_name, self.user.last_name])

    def get_absolute_url(self):
        return reverse('people:profile', kwargs={'slug': self.slug})


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


def init_profile_from_ldap(user, ldapinfo):
    '''Extra user/profile init logic for auto-populating people
    profile fields with data available in LDAP.'''
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=user)

    # populate profile with data we can pull from ldap
    # - set user's display name as page title
    profile.title = str(ldapinfo.displayName)
    # - generate a slug based on display name
    profile.slug = slugify(ldapinfo.displayName)
    profile.phone_number = str(ldapinfo.telephoneNumber)
    # 'street' in ldap is office location
    profile.office_location = str(ldapinfo.street)
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

