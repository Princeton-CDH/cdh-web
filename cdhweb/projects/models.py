from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from mezzanine.core.fields import RichTextField, FileField
from mezzanine.core.models import Displayable
from mezzanine.core.managers import DisplayableManager
from mezzanine.utils.models import AdminThumbMixin, upload_to
from taggit.managers import TaggableManager

from cdhweb.resources.models import ResourceType


class ProjectQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def current(self):
        today = timezone.now()
        # current projects means an active grant
        # filter for projects with grants where start and end date
        # come before and after the current date
        return self.filter(grant__start_date__lt=today) \
            .filter(grant__end_date__gt=today)


class ProjectManager(DisplayableManager):
    # extend displayable manager to preserve access to published filter
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def current(self):
        return self.get_queryset().current()


class Project(Displayable, AdminThumbMixin):
    short_description = models.CharField(max_length=255)
    long_description = RichTextField()
    is_active = models.BooleanField(default=False)

    members = models.ManyToManyField(User, through='Membership')
    resources = models.ManyToManyField(ResourceType, through='ProjectResource')

    tags = TaggableManager(blank=True)

    # TODO: include help text to indicate images are optional, where they
    # are used (size?); add language about putting large images in the
    # body of the project description, when we have styles for that.
    image = FileField(verbose_name="Image",
        upload_to=upload_to("projects.image", "projects"),
        format="Image", max_length=255, null=True, blank=True)

    thumb = FileField(verbose_name="Thumbnail",
        upload_to=upload_to("projects.image", "projects"),
        format="Image", max_length=255, null=True, blank=True)

    # custom manager and queryset
    objects = ProjectManager()

    admin_thumb_field = "thumb"

    class Meta:
        # sort by project title for now
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project:detail', kwargs={'slug': self.slug})


class GrantType(models.Model):
    grant_type = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.grant_type


class Grant(models.Model):
    project = models.ForeignKey(Project)
    grant_type = models.ForeignKey(GrantType)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '%s: %s (%s-%s)' % (self.project.title, self.grant_type.grant_type,
            self.start_date.year, self.end_date.year)


# fixme: where does resource type go, for associated links?

class Role(models.Model):
    title = models.CharField(max_length=255, unique=True)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
        null=False)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title


class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    grant = models.ForeignKey(Grant)
    role = models.ForeignKey(Role)

    def __str__(self):
        return '%s - %s on %s' % (self.user, self.role, self.grant)


class ProjectResource(models.Model):
    '''Through-model for associating projects with resource types and
    URLs'''
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    URL = models.URLField()