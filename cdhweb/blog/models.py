from django.db import models
from django.urls import reverse
from django.utils.dateformat import format
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.models import Orderable, Page, PageManager, PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from cdhweb.pages.models import BasePage, LinkPage, PagePreviewDescriptionMixin
from cdhweb.people.models import Person


class Author(Orderable):
    """Ordered relationship between Person and BlogPost."""

    post = ParentalKey("blog.BlogPost", related_name="authors")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    panels = [FieldPanel("person")]

    def __str__(self) -> str:
        return "%s on %s" % (self.person, self.post)


class BlogPostQuerySet(PageQuerySet):
    def recent(self):
        """Order blog posts by date published."""
        # NOTE we can't use ordering on the model to do this by default, so we
        # have to make sure to call this method instead. See:
        # https://docs.wagtail.io/en/stable/topics/pages.html#page-queryset-ordering
        return self.order_by("-first_published_at")

    def featured(self):
        """return blog posts that are marked as featured"""
        return self.filter(featured=True)


# custom manager for wagtail pages, see:
# https://docs.wagtail.io/en/stable/topics/pages.html#custom-page-managers
BlogPostManager = PageManager.from_queryset(BlogPostQuerySet)


class BlogPostTag(TaggedItemBase):
    """Tags for Blog posts."""

    content_object = ParentalKey(
        "blog.BlogPost", on_delete=models.CASCADE, related_name="tagged_items"
    )


class BlogPost(BasePage, ClusterableModel, PagePreviewDescriptionMixin):
    """A Blog post, implemented as a Wagtail page."""

    featured_image = models.ForeignKey(
        "wagtailimages.image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Appears on the homepage carousel when post is featured.",
    )
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    featured = models.BooleanField(
        default=False, help_text="Show the post in the carousel on the homepage."
    )
    people = models.ManyToManyField(Person, through="blog.Author", related_name="posts")

    # can only be created underneath special link page
    parent_page_types = ["blog.BlogLinkPage"]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = Page.content_panels + [
        FieldRowPanel((ImageChooserPanel("featured_image"), FieldPanel("featured"))),
        FieldPanel("description"),
        MultiFieldPanel((InlinePanel("authors", label="Author"),), heading="Authors"),
        StreamFieldPanel("body"),
        StreamFieldPanel("attachments"),
    ]
    promote_panels = Page.promote_panels + [FieldPanel("tags")]

    # index description in addition to body content
    search_fields = BasePage.search_fields + [index.SearchField('description')]

    # custom manager/queryset logic
    objects = BlogPostManager()

    # configure template path for wagtail preview
    template = "blog/blogpost_detail.html"

    @property
    def short_title(self):
        """Shorter title with ellipsis."""
        return Truncator(self.title).chars(65)

    @property
    def short_description(self):
        """Shorter description with ellipsis."""
        return Truncator(self.get_description()).chars(250)

    @property
    def author_list(self):
        """Comma-separated list of author names."""
        return ", ".join(str(author.person) for author in self.authors.all())

    def __str__(self):
        return '"%s" (%s)' % (
            self.short_title,
            format(self.first_published_at, "F j, Y"),
        )

    def get_url_parts(self, *args, **kwargs):
        """Custom blog post URLs of the form /updates/2014/03/01/my-post."""
        url_parts = super().get_url_parts(*args, **kwargs)
        # NOTE evidently these can sometimes be None; unclear why – perhaps it
        # gets called in a context where the request is unavailable. Seems to
        # happen immediately on page creation; the creation still succeeds.
        if url_parts and self.first_published_at:
            site_id, root_url, _ = url_parts
            page_path = reverse(
                "blog:detail",
                kwargs={
                    "year": self.first_published_at.year,
                    # force two-digit month and day
                    "month": "%02d" % self.first_published_at.month,
                    "day": "%02d" % self.first_published_at.day,
                    "slug": self.slug,
                },
            )
            return site_id, root_url, page_path

    def get_sitemap_urls(self, request):
        """Override sitemap listings to add priority for featured posts."""
        # output is a list of dict; there should only ever be one element. see:
        # https://docs.wagtail.io/en/stable/reference/contrib/sitemaps.html#urls
        urls = super().get_sitemap_urls(request=request)
        if self.featured:
            urls[0]["priority"] = 0.6  # default is 0.5; slight increase
        return urls


class BlogLinkPage(LinkPage):
    """Container page that defines where blog posts can be created."""

    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is a BlogPost; this is so that
    # Events made in the admin automatically are created here.
    subpage_types = [BlogPost]
