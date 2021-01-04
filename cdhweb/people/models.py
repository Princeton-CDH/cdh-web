from datetime import date

from cdhweb.pages.models import BodyContentBlock
from cdhweb.resources.models import (Attachment, DateRange,
                                     PublishedQuerySetMixin)
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from mezzanine.core.fields import FileField
from mezzanine.core.fields import RichTextField as MezzanineRichTextField
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED, Displayable)
from mezzanine.utils.models import AdminThumbMixin, upload_to
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel


class Title(models.Model):
    '''Job titles for people'''
    title = models.CharField(max_length=255, unique=True)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
                                             null=False)
    positions = models.ManyToManyField("people.Person", through='Position')

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title

    def num_people(self):
        '''Number of people with this position title'''
        # NOTE: maybe more meaningful if count restrict to _current_ titles?
        return self.positions.distinct().count()
    num_people.short_description = '# People'


class Person(ClusterableModel):
    # in cdhweb 2.x this was a proxy model for User;
    # in 3.x it is a distinct model with 1-1 optional relationship to User
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Corresponding user account for this person (optional)'
    )
    cdh_staff = models.BooleanField(
        'CDH Staff',
        default=False,
        help_text='CDH staff or Postdoctoral Fellow.')
    job_title = models.CharField(
        max_length=255, blank=True,
        help_text='Professional title, e.g. Professor or Assistant Professor')
    department = models.CharField(
        max_length=255, blank=True,
        help_text='Academic Department at Princeton or other institution')
    institution = models.CharField(
        max_length=255, blank=True,
        help_text='Institutional affiliation (for people not associated with Princeton)')
    phone_number = models.CharField(
        max_length=50, blank=True, help_text="Office phone number")
    office_location = models.CharField(
        max_length=255, blank=True, help_text="Office number and building")

    PU_STATUS_CHOICES = (
        ('fac', 'Faculty'),
        ('stf', 'Staff'),
        ('graduate', 'Graduate Student'),
        ('undergraduate', 'Undergraduate Student'),
        ('external', 'Not associated with Princeton')
    )
    pu_status = models.CharField('Princeton Status', choices=PU_STATUS_CHOICES,
                                 max_length=15, blank=True, default='')

    image = models.ForeignKey('wagtailimages.image', null=True,
                              blank=True, on_delete=models.SET_NULL,
                              related_name='+')  # no reverse relationship

    #: update timestamp
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    # wagtail admin setup
    panels = [
        ImageChooserPanel("image"),
        FieldRowPanel((FieldPanel("first_name"),
                       FieldPanel("last_name")), "Name"),
        FieldPanel("user"),
        FieldRowPanel((FieldPanel("pu_status"),
                       FieldPanel("cdh_staff")), "Status"),
        MultiFieldPanel((
            FieldPanel("job_title"),
            FieldPanel("department"),
            FieldPanel("institution"),
            FieldPanel("phone_number"),
            FieldPanel("office_location"),
        ), heading="Employment"),
        InlinePanel("positions", heading="Positions"),
    ]

    class Meta:
        verbose_name_plural = "people"

    def __str__(self):
        """Person display for listing in admin menus. Uses first and last name
        if set, otherwise falls back to username. If no user, uses pk as a last
        resort."""
        if self.first_name or self.last_name:
            return " ".join([self.first_name, self.last_name]).strip()
        if self.user:
            return self.user.username
        return "Person %d" % self.pk

    @property
    def current_title(self):
        """Return the first of any non-expired titles held by this Person."""
        current_positions = self.positions.filter(end_date__isnull=True)
        if current_positions.exists():
            return current_positions.first().title

    @receiver(pre_delete, sender="people.Person")
    def cleanup_profile(sender, **kwargs):
        """Handler to delete the corresponding profile on Person deletion."""
        # NOTE wagtail doesn't support cascading deletes to pages because it
        # corrupts the page tree, and it's unclear what handler is best to use.
        # We use PROTECT on the target and handle it here instead. See:
        # https://github.com/wagtail/wagtail/issues/1602
        try:
            ProfilePage.objects.get(person=kwargs["instance"]).delete()
        except ProfilePage.DoesNotExist:
            pass

    @receiver(pre_save, sender="people.Person")
    def set_profile_title(sender, **kwargs):
        """Handler to update ProfilePage titles when the Person is updated."""
        # Call save() on the ProfilePage so it updates its title
        try:
            ProfilePage.objects.get(person=kwargs["instance"]).save()
        except ProfilePage.DoesNotExist:
            pass


class ProfileQuerySet(PublishedQuerySetMixin):

    #: position titles that indicate a person is a postdoc
    postdoc_titles = ['Postdoctoral Fellow',
                      'Postdoctoral Fellow and Communications Lead']

    #: position titles that indicate a person is a project director
    director_roles = ['Project Director', 'Co-PI: Research Lead']

    #: position titles that indicate a staff person is a student
    student_titles = ['Graduate Fellow', 'Graduate Assistant',
                      'Undergraduate Assistant',
                      'Postgraduate Research Associate']
    #: memebership roles that indicate someone is an affiliate
    project_roles = ['Project Director',
                     'Project Manager', 'Co-PI: Research Lead']

    #: student status codes from LDAP
    student_pu_status = ['graduate', 'undergraduate']

    #: executive committee member titles
    exec_member_title = 'Executive Committee Member'
    with_exec_title = 'Sits with Executive Committee'
    exec_committee_titles = [exec_member_title, with_exec_title]

    def staff(self):
        '''Return only CDH staff members'''
        return self.filter(is_staff=True)

    def student_affiliates(self):
        '''Return CDH student staff members, grantees, and PGRAs based on
        Project Director or Project Manager role.'''
        return self \
            .filter(models.Q(pu_status__in=self.student_pu_status) |
                    models.Q(user__positions__title__title__in=self.student_titles)) \
            .filter(models.Q(is_staff=True) |
                    models.Q(user__membership__role__title__in=self.project_roles)) \
            .exclude(pu_status="stf")

    def not_students(self):
        '''Filter out students based on PU status'''
        return self \
            .exclude(pu_status__in=self.student_pu_status)

    def affiliates(self):
        '''Faculty and staff affiliates based on PU status and Project Director
        project role. Excludes CDH staff.'''
        return self.filter(pu_status__in=('fac', 'stf'),
                           user__membership__role__title__in=self.director_roles) \
            .exclude(is_staff=True)

    def executive_committee(self):
        '''Executive committee members; based on position title.'''
        return self.filter(user__positions__title__title__in=self.exec_committee_titles)

    def exec_member(self):
        '''Executive committee members'''
        return self.filter(user__positions__title__title=self.exec_member_title)

    def sits_with_exec(self):
        '''Non-faculty Executive committee members'''
        return self.filter(user__positions__title__title=self.with_exec_title)

    def grant_years(self):
        '''Annotate with first start and last end grant year for grants
        that a person was project director.'''
        # NOTE: filters within the aggregation query on project director
        # but not on the entire query so that e.g. on the students
        # page student staff without grants are still included
        return self.annotate(
            first_start=models.Min(models.Case(
                models.When(user__membership__role__title__in=self.director_roles,
                            then='user__membership__start_date'))),
            last_end=models.Max(models.Case(
                models.When(user__membership__role__title__in=self.director_roles,
                            then='user__membership__end_date'))))

    def project_manager_years(self):
        '''Annotate with first start and last end grant year for grants
        that a person was project manager.'''
        # NOTE: filters within the aggregation query on project manager
        # but not on the entire query so that e.g. on the students
        # page student staff without grants are still included
        return self.annotate(
            pm_start=models.Min(models.Case(
                models.When(user__membership__role__title='Project Manager',
                            then='user__membership__start_date'))),
            pm_end=models.Max(models.Case(
                models.When(user__membership__role__title='Project Manager',
                            then='user__membership__end_date'))))

    def speakers(self):
        '''Return external speakers at CDH events.'''
        # Speakers are non-Princeton profiles (external) who are associated with
        # at least one published event
        return self.filter(user__event__isnull=False, pu_status='external',
                           user__event__status=CONTENT_STATUS_PUBLISHED)

    def _current_position_query(self):
        # query to find a user with a current cdh position
        # user *has* a position and it has no end date or date after today
        return (
            models.Q(user__positions__isnull=False) &
            (models.Q(user__positions__end_date__isnull=True) |
             models.Q(user__positions__end_date__gte=date.today())
             )
        )

    def _current_project_member_query(self):
        today = timezone.now()
        return (
            # in one of the allowed roles (project director/project manager)
            models.Q(user__membership__role__title__in=self.project_roles) &
            # current based on membership dates
            (
                models.Q(user__membership__start_date__lte=today) &
                (models.Q(user__membership__end_date__gte=today) |
                 models.Q(user__membership__end_date__isnull=True))
            )
        )

    def current(self):
        '''Return profiles for users with a current position or current grant
        based on start and end dates.'''
        # annotate with an is_current flag to make template logic simpler
        return self.filter(models.Q(self._current_position_query()) |
                           models.Q(self._current_project_member_query())) \
                   .extra(select={'is_current': True})
        # NOTE: couldn't get annotate to work
        # .annotate(is_current=models.Value(True, output_field=models.BooleanField))

    def current_grant(self):
        '''Return profiles for users with a current grant.'''
        return self.filter(self._current_project_member_query())

    def current_position(self):
        '''Return profiles for users with a current position.'''
        return self.filter(self._current_position_query())

    def current_position_nonexec(self):
        '''Return profiles for users with a current position, excluding
        executive committee positions.'''
        return self.filter(models.Q(self._current_position_query()) &
                           ~models.Q(user__positions__title__title__in=self.exec_committee_titles))

    def has_upcoming_events(self):
        '''Filter profiles to only those with an upcoming published event.'''
        return self.filter(user__event__end_time__gte=timezone.now(),
                           user__event__status=CONTENT_STATUS_PUBLISHED).distinct()

    def order_by_event(self):
        '''Order by earliest published event associated with profile.'''
        return self.annotate(
            earliest_event=models.Min(models.Case(
                models.When(user__event__status=CONTENT_STATUS_PUBLISHED,
                            then='user__event__start_time')))
        ).order_by('earliest_event')

    def order_by_position(self):
        '''order by job title sort order and then by start date'''
        # annotate to avoid duplicates in the queryset due to multiple positions
        # sort on highest position title (= lowest number) and earliest start date (may
        # not be from the same position)
        return self.annotate(min_title=models.Min('user__positions__title__sort_order'),
                             min_start=models.Min('user__positions__start_date')) \
            .order_by('min_title', 'min_start', 'user__last_name')


class Profile(Displayable, AdminThumbMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # -> cdh_staff on person
    is_staff = models.BooleanField(
        default=False,
        help_text='CDH staff or Postdoctoral Fellow. If checked, person ' +
        'will be listed on the CDH staff page and will have a profile page ' +
        'on the site.')
    education = MezzanineRichTextField()
    bio = MezzanineRichTextField()
    # NOTE: could use regex here, but how standard are staff phone
    # numbers? or django-phonenumber-field, but that's probably overkill
    phone_number = models.CharField(max_length=50, blank=True)
    office_location = models.CharField(max_length=255, blank=True)

    # moved to person
    job_title = models.CharField(
        max_length=255, blank=True,
        help_text='Professional title, e.g. Professor or Assistant Professor')
    department = models.CharField(
        max_length=255, blank=True,
        help_text='Academic Department at Princeton or other institution (optional)')
    institution = models.CharField(
        max_length=255, blank=True,
        help_text='Institutional affiliation (for people not associated with Princeton)')

    PU_STATUS_CHOICES = (
        ('fac', 'Faculty'),
        ('stf', 'Staff'),
        ('graduate', 'Graduate Student'),
        ('undergraduate', 'Undergraduate Student'),
        ('external', 'Not associated with Princeton')
    )
    pu_status = models.CharField('Princeton Status', choices=PU_STATUS_CHOICES,
                                 max_length=15, blank=True, default='')

    image = FileField(verbose_name="Image",
                      upload_to=upload_to("people.image", "people"),
                      format="Image", max_length=255, null=True, blank=True)

    thumb = FileField(verbose_name="Thumbnail",
                      upload_to=upload_to("people.image", "people/thumbnails"),
                      format="Image", max_length=255, null=True, blank=True)

    admin_thumb_field = "thumb"

    attachments = models.ManyToManyField(Attachment, blank=True)

    # TODO: check for
    tags = TaggableManager(blank=True)

    # custom manager for additional queryset filters
    objects = ProfileQuerySet.as_manager()

    class Meta:
        ordering = ["-user__last_name"]

    def __str__(self):
        # use title if set
        return self.title or \
            ' '.join([self.user.first_name, self.user.last_name])

    def get_absolute_url(self):
        return reverse('people:profile', kwargs={'slug': self.slug})

    @property
    def current_title(self):
        # FIXME: dowe actually need this here?
        return self.user.current_title


class ProfilePage(Page):
    """Profile page for a Person, managed via wagtail."""
    person = models.OneToOneField(
        Person, help_text="Corresponding person for this profile",
        on_delete=models.PROTECT)  # See NOTE + delete handler on Person
    image = models.ForeignKey('wagtailimages.image', null=True,
                              blank=True, on_delete=models.SET_NULL,
                              related_name='+')  # no reverse relationship
    education = RichTextField(blank=True)
    bio = StreamField(BodyContentBlock, blank=True)

    # admin edit configuration
    content_panels = [
        FieldRowPanel(
            (FieldPanel("person"), ImageChooserPanel("image")), "Person"),
        FieldPanel("education"),
        StreamFieldPanel("bio")
    ]

    parent_page_types = ["cdhpages.PeopleLandingPage"]
    subpage_types = []

    def save(self, *args, **kwargs):
        """Set the page title automatically."""
        # Use Person's name as page title
        self.title = str(self.person)
        return super().save(*args, **kwargs)


class Position(DateRange):
    '''Through model for many-to-many relation between people
    and titles.  Adds start and end dates to the join table.'''
    person = ParentalKey(Person, on_delete=models.CASCADE,
                         related_name="positions")
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return '%s %s (%s)' % (self.person, self.title, self.start_date.year)


def init_person_from_ldap(user, ldapinfo):
    '''Extra User init logic for creating and auto-populating a corresponding
    Person with data from LDAP.'''

    # update User to use ldap email
    user.email = user.email.lower()
    user.save()

    # populate Person fields with data we can pull from ldap, if they are empty
    person, _created = Person.objects.get_or_create(user=user)

    # set first/last name basic on basic whitespace split; can adjust later
    first_name, *_others, last_name = str(ldapinfo.displayName).split()
    person.first_name = person.first_name or first_name
    person.last_name = person.last_name or last_name

    # set phone number
    if ldapinfo.telephoneNumber and not person.phone_number:
        person.phone_number = str(ldapinfo.telephoneNumber)

    # set office location ("street" in ldap)
    if ldapinfo.street and not person.office_location:
        person.office_location = str(ldapinfo.street)

    # set department (organizational unit or "ou" in ldap)
    if ldapinfo.ou and not person.department:
        person.department = str(ldapinfo.ou)

    # set job title (split and use only first portion from ldap)
    # NOTE titles for cdh staff are managed via Title/Position instead
    if ldapinfo.title and not person.job_title:
        person.job_title = str(ldapinfo.title).split(",")[0]

    # always update PU status to current
    person.pu_status = str(ldapinfo.pustatus)
    person.save()
