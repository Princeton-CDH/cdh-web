from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator

from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, RichText
from mezzanine.utils.models import AdminThumbMixin, upload_to

from taggit.managers import TaggableManager

# from cdhweb.people.models import Person
from cdhweb.resources.models import Attachment, PublishedQuerySetMixin


class MultiOwnable(models.Model):
    """
    Abstract model based on Mezzanine's :class:`mezzanine.core.models.Ownable`
    to provides ownership of an object for a user, except allows for
    multiple owners.
    """

    users = models.ManyToManyField(User, verbose_name=_("Authors"),
        related_name="%(class)ss")

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or \
            self.users.filter(id=request.user.id).exists()

    def author_list(self):
        '''comma-separated list of authors'''
        return ', '.join(str(user) for user in self.users.all())
    author_list.short_description = 'Authors'


class BlogPostQuerySet(PublishedQuerySetMixin):

    def featured(self):
        '''return blog posts that are marked as featured'''
        return self.filter(is_featured=True)

    def recent(self):
        '''sort blog posts by publication date'''
        return self.order_by('-publish_date')


class BlogPost(Displayable, MultiOwnable, RichText, AdminThumbMixin):
    """
    A blog post with multiple authors. Based on
    :class:`mezzanine.blog.models.BlogPost`.
    """

    # mezzanine blogpost has comments, categoriees, and ratings; do we
    # care about any of those?
    featured_image = FileField(verbose_name=_("Featured Image"),
        upload_to=upload_to("blog.BlogPost.featured_image", "blog"),
        help_text="Appears on the homepage carousel when post is featured.",
        format="Image", max_length=255, null=True, blank=True)
    related_posts = models.ManyToManyField("self",
                                 verbose_name=_("Related posts"), blank=True)
    tags = TaggableManager(blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)
    is_featured = models.BooleanField(verbose_name=_("Featured"), default=False,
                help_text="Feature the post in the carousel on the homepage.")

    admin_thumb_field = "featured_image"

    @property
    def short_title(self):
        '''shorter title with ellipsis'''
        return Truncator(self.title).chars(65)

    @property
    def short_description(self):
        '''shorter description with ellipsis'''
        return Truncator(self.description).chars(250)

    # custom manager for additioal queryset filters
    objects = BlogPostQuerySet.as_manager()

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ("-publish_date",)

    def get_absolute_url(self):
        # we don't have to worry about the various url config options
        # that mezzanine has to support; just handle the url style we
        # want to use locally
        return reverse('blog:detail', kwargs={
            'year': self.publish_date.year,
            # force two-digit month
            'month': '%02d' % self.publish_date.month,
            'day': '%02d' % self.publish_date.day,
            'slug': self.slug})