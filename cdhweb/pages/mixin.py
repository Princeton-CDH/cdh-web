from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    TitleFieldPanel,
)
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from cdhweb.constants import NOHEADINGS_FEATURES

from .utils import (
    LengthOverrideWidget,
    absolutize_url,
    get_default_preview_img_url,
    get_first_of,
)


class HomePageHeroMixin(models.Model):
    summary = models.TextField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Page Summary",
        help_text="Text that supports / qualifies the hero header and gives people a sense of who you are",
    )

    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that conveys sense of site / brand",
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel(
                    "title",
                    help_text=""" Heading on the larger hero banner at top of the page.
                                Ideal length < 45 characters (around 5 words)""",
                    widget=LengthOverrideWidget(max_length=80),
                ),
                FieldPanel("summary"),
                FieldPanel("hero_image"),
            ],
            "HomePage Hero",
        )
    ]

    class Meta:
        abstract = True


class StandardHeroMixinNoImage(models.Model):
    description = RichTextField(
        max_length=200,
        blank=True,
        null=True,
        features=["bold", "italic"],
        verbose_name="Page Summary",
        help_text="""Short introduction to the page, aim for max two clear sentences (max. 200 chars). 
        Used to orient the user and help them identify relevancy of the page to meet their needs. """,
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel(
                    "title",
                    help_text="""Main heading for the page. Ideally up to five words long (max.100 chars).""",
                    widget=LengthOverrideWidget(max_length=100),
                ),
                FieldPanel("description"),
            ],
            "Standard Hero",
        )
    ]

    search_fields = Page.search_fields + [
        index.SearchField("description"),
    ]

    @cached_property
    def breadcrumbs(self):
        ancestors = self.get_ancestors().live().public().specific()
        return ancestors[1:]  # removing root

    class Meta:
        abstract = True


class IndexPageMixin(StandardHeroMixinNoImage):
    class Meta:
        abstract = True

    preface = RichTextField(
        blank=True,
        features=NOHEADINGS_FEATURES,
        help_text="""
            Text that sits between the description and the child-page listing
        """,
    )

    search_fields = StandardHeroMixinNoImage.search_fields + [
        index.SearchField("preface")
    ]

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel(
                    "title",
                    help_text="""Main heading for the page. Ideally up to five words long (max.100 chars).""",
                    widget=LengthOverrideWidget(max_length=100),
                ),
                FieldPanel("description"),
                FieldPanel("preface"),
            ],
            "Standard Hero",
        )
    ]


class StandardHeroMixin(StandardHeroMixinNoImage):
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional image to support intent of the page.",
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel(
                    "title",
                    help_text="""Main heading for the page. Ideally up to five words long (max.100 chars).""",
                    widget=LengthOverrideWidget(max_length=100),
                ),
                FieldPanel("description"),
                FieldPanel("hero_image"),
            ],
            "Standard Hero",
        )
    ]

    class Meta:
        abstract = True


class SidebarNavigationMixin(models.Model):
    disable_sidebar = models.BooleanField(
        default=False,
        help_text="Hide the sidebar menu showing siblings of this page.",
    )

    @cached_property
    def sidebar_navigation(self):
        """
        Display a Sidebar menu of Page siblings at L2 or deeper unless disabled.
        This assumes all siblings inherit nav properties inherited from PromoteMixin
        """

        if self.disable_sidebar or self.depth <= 3:
            return None  # only show sidebar for pages greater than level 3 (Homepage is level 1)

        siblings = Page.objects.sibling_of(self).live().in_menu().public().specific()

        if not siblings.exclude(pk=self.pk).exists():
            return None  # no siblings so don't create side bar

        return [
            {
                "title": page.title,
                "url": page.get_url(),
                "active": True if page.pk == self.pk else False,
            }
            for page in siblings
        ]

    settings_panels = [
        FieldRowPanel(
            [
                FieldPanel("disable_sidebar"),
            ]
        )
    ]

    class Meta:
        abstract = True


class OpenGraphMixin(models.Model):
    class Meta:
        abstract = True

    @cached_property
    def og_image_url(self):
        image = get_first_of(self, "feed_image", "image", "hero_image")
        if not image:
            return get_default_preview_img_url()

        rendition = image.get_rendition("fill-1200x627")
        return absolutize_url(rendition.url)
