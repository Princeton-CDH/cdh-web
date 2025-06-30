import bleach
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page, PageManager, PageQuerySet
from wagtail.search import index
from wagtailautocomplete.edit_handlers import AutocompletePanel

from cdhweb.pages.mixin import IndexPageMixin, StandardHeroMixinNoImage
from cdhweb.pages.models import BasePage, ContentPage, LinkPage
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


class BlogPost(BasePage, ClusterableModel):
    """A Blog post, implemented as a Wagtail page."""

    template = "blog/blog_post.html"

    description = RichTextField(
        max_length=200,
        blank=True,
        null=True,
        features=["bold", "italic"],
        verbose_name="Blog description",
        help_text="Short introduction to the page, aim for max two clear sentences (max. 200 chars).",
    )

    image = models.ForeignKey(
        "wagtailimages.image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Appears on the homepage carousel when post is featured.",
    )
    caption = RichTextField(
        features=[
            "italic",
            "bold",
            "link",
        ],
        help_text="A short caption for the image.",
        blank=True,
        max_length=180,
    )

    credit = RichTextField(
        features=[
            "italic",
            "bold",
            "link",
        ],
        help_text="A credit line or attribution for the image.",
        blank=True,
        max_length=80,
    )

    alt_text = models.CharField(
        help_text="Describe the image for screen readers",
        blank=True,
        max_length=80,
    )
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    featured = models.BooleanField(
        default=False, help_text="Show the post in the carousel on the homepage."
    )
    people = models.ManyToManyField(Person, through="blog.Author", related_name="posts")

    category = models.CharField(
        verbose_name="Category",
        help_text="Category tag to display on tile",
        blank=True,
        max_length=20,
    )

    publish_date = models.DateField(
        verbose_name="Publish Date",
        help_text="Publish date to display for this post. Leave blank to use the date the post was first published.",
        blank=True,
        null=True,
    )

    # can only be created underneath special link page
    parent_page_types = ["blog.BlogLinkPageArchived", "blog.BlogLandingPage"]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("publish_date"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("caption"),
                FieldPanel("credit"),
                FieldPanel("alt_text"),
            ],
            heading="Hero Image",
        ),
        MultiFieldPanel(
            [InlinePanel("authors", [AutocompletePanel("person")], label="Author")],
            heading="Authors",
        ),
        FieldPanel("category"),
        FieldPanel("body"),
        FieldPanel("attachments"),
    ]
    promote_panels = (
        [
            MultiFieldPanel(
                [
                    FieldPanel("short_title"),
                    FieldPanel("short_description"),
                    FieldPanel("feed_image"),
                ],
                "Share Page",
            ),
        ]
        + BasePage.promote_panels
        + [FieldPanel("tags")]
    )

    # index description in addition to body content
    search_fields = BasePage.search_fields + [
        index.SearchField("description"),
        index.RelatedFields(
            "people",
            [
                index.SearchField("first_name"),
                index.SearchField("last_name"),
            ],
        ),
    ]

    # custom manager/queryset logic
    objects = BlogPostManager()

    @cached_property
    def breadcrumbs(self):
        ancestors = self.get_ancestors().live().public().specific()
        return ancestors[1:]  # removing root

    @property
    def author_list(self):
        """Comma-separated list of author names."""
        return ", ".join(str(author.person) for author in self.authors.all())

    @property
    def display_date(self):
        """Return the custom date if set, otherwise return first_published_at."""
        if self.publish_date:
            return self.publish_date
        return self.first_published_at.date() if self.first_published_at else None

    def get_url_parts(self, request, *args, **kwargs):
        """Custom blog post URLs of the form /updates/2014/03/01/my-post."""
        url_parts = super().get_url_parts(request, *args, **kwargs)
        # NOTE evidently these can sometimes be None; unclear why – perhaps it
        # gets called in a context where the request is unavailable. Seems to
        # happen immediately on page creation; the creation still succeeds.
        if url_parts and self.first_published_at:
            site_id, root_url, _remainder = url_parts
            parent = self.get_parent().specific

            # If for some reason we don't have a bloglanding-style parent, just
            # use `super()`
            if not hasattr(parent, "reverse_subpage"):
                return url_parts

            # These dates need to be in DEFAULT_TIMEZONE, rather than UTC,
            # otherwise the dates don't match up with the generated URLs (in
            # `BlogPage.get_url_parts`)
            path_date = timezone.localtime(self.first_published_at)
            page_path = parent.reverse_subpage(
                "dated_child",
                kwargs={
                    "year": path_date.year,
                    # force two-digit month and day
                    "month": "%02d" % path_date.month,
                    "day": "%02d" % path_date.day,
                    "slug": self.slug,
                },
            )
            return site_id, root_url, parent.get_url(request) + page_path

    def get_sitemap_urls(self, request):
        """Override sitemap listings to add priority for featured posts."""
        # output is a list of dict; there should only ever be one element. see:
        # https://docs.wagtail.io/en/stable/reference/contrib/sitemaps.html#urls
        urls = super().get_sitemap_urls(request=request)
        if self.featured:
            urls[0]["priority"] = 0.6  # default is 0.5; slight increase
        return urls


class BlogLinkPageArchived(LinkPage):
    """Container page that defines where blog posts can be created."""

    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is a BlogPost; this is so that
    # Events made in the admin automatically are created here.
    subpage_types = [BlogPost]


class BlogLandingPage(IndexPageMixin, RoutablePageMixin, Page):
    """Container page that defines where Event pages can be created."""

    featured_post = models.ForeignKey(
        "BlogPost",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="featured_post",
    )

    page_size = 12
    template_name = "blog/blog_landing_page.html"

    content_panels = IndexPageMixin.content_panels + [FieldPanel("featured_post")]

    search_fields = IndexPageMixin.search_fields

    settings_panels = Page.settings_panels

    subpage_types = [BlogPost, ContentPage]

    def get_context(self, request, year=None, month=None):
        context = super().get_context(request)

        if year:
            posts = self.get_posts_for_year_and_month(year=year, month=month)
        else:
            posts = self.get_latest_posts()

        posts = posts.prefetch_related("image", "image__renditions")

        # Exclude featured_post from the results, and add
        # it to the context note this means the template
        # should access `featured_post` *NOT*
        # `self.featured_post`
        if self.featured_post and posts.filter(id=self.featured_post_id).exists():
            context["featured_post"] = self.featured_post
            posts = posts.exclude(pk=self.featured_post.pk)

        page_number = request.GET.get("page") or 1
        paginator = Paginator(posts, self.page_size)
        page = paginator.page(page_number)
        context.update(
            {
                "paginator": paginator,
                "is_paginated": page.has_other_pages(),
                "page_obj": page,  # Used in pagination template
                "posts": page,  # Used in page template
            }
        )

        context["date_list"] = self.get_list_of_dates()

        return context

    @path("<int:year>/", name="by-year")
    @path("<int:year>/<int:month>/", name="by-month")
    def by_date(self, request, year=None, month=None):
        context = self.get_context(request, year=year, month=month)
        return self.render(request, context_overrides=context)

    @path("<int:year>/<int:month>/<int:day>/<slug:slug>/", name="dated_child")
    def dated_child(self, request, year=None, month=None, day=None, slug=None):
        child = get_object_or_404(
            self.get_children()
            .live()
            .public()
            .filter(
                first_published_at__year=year,
                first_published_at__month=month,
                first_published_at__day=day,
            ),
            slug=slug,
        )
        return child.specific.serve(request)

    def get_posts_for_year_and_month(self, year=None, month=None):
        # get blogs by year and month
        child_qs = self.get_latest_posts().filter(first_published_at__year=year)
        if month:
            child_qs = child_qs.filter(first_published_at__month=month)
        return child_qs

    def get_latest_posts(self):
        child_pages = self.get_children().live().public().specific()

        # Fetch all posts ordered by most recently published
        return child_pages.order_by("-first_published_at")

    def get_list_of_dates(self):
        # get list of dates to sort by

        child_pages = self.get_children().live()
        return child_pages.dates("first_published_at", "month", order="DESC")
