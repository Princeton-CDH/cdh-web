from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from mezzanine.core.fields import FileField
from mezzanine.core.models import RichText, CONTENT_STATUS_PUBLISHED
from mezzanine.pages.models import Page
from mezzanine.utils.models import upload_to


class ResourceType(models.Model):
    '''Resource type for associating particular kinds of URLs
    with people and projects (e.g., project url, GitHub, Twitter, etc)'''
    name = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
        null=False)
    # NOTE: defining the relationship here since we can't add to it to
    # django's auth.User directly
    users = models.ManyToManyField(User, through='UserResource',
        related_name='resources')

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class ExcerptMixin(object):

    def excerpt(self):
        '''Content excerpt. Returns description only if it is not
        auto-generated, since generated description will be redundant
        when displayed on the page.'''
        if not self.gen_description:
            return self.description



class UserResource(models.Model):
    '''Through-model for associating users with resource types and
    corresponding URLs for the specified resource type.'''
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()


class Attachment(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    file = FileField('Document', blank=True,
        upload_to=upload_to("resources.documents", "documents"))
    url = models.URLField(blank=True)
    # TODO: needs validation to ensure one and only one of
    # file and url is set
    PDF = 'PDF'
    MSWORD = 'DOC'
    VIDEO = 'VIDEO'
    URL = 'URL'
    type_choices = (
        (PDF, 'PDF Document'),
        (MSWORD, 'MS Word Document'),
        (VIDEO, 'Video'),
        (URL, 'URL'),
    )
    attachment_type = models.CharField(max_length=255, choices=type_choices)

    pages = models.ManyToManyField(Page, related_name='attachments', blank=True)

    def __str__(self):
        parts = [self.title]
        if self.author:
            parts.append(', %s' % self.author)
        if self.attachment_type:
            parts.append(' (%s)' % self.attachment_type)
        return ''.join(parts)


class LandingPage(Page, RichText):
    tagline = models.CharField(max_length=255)
    image = FileField(verbose_name="Image",
        upload_to=upload_to("resources.landing_pages.image", "resources"),
        format="Image", max_length=255, null=True, blank=True)


class PublishedQuerySetMixin(models.QuerySet):
    '''QuerySet mixin. Adds a filter to find published content.
    Uses the published check from
     :class:`mezzanine.core.managers.PublishedManager`.'''

    def published(self, for_user=None):
        """
        For non-staff users, return items with a published status and
        whose publish and expiry dates fall before and after the
        current date when specified.
        """
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(
            models.Q(publish_date__lte=now()) | models.Q(publish_date__isnull=True),
            models.Q(expiry_date__gte=now()) | models.Q(expiry_date__isnull=True),
            models.Q(status=CONTENT_STATUS_PUBLISHED))

