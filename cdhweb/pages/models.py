from random import shuffle

import bleach
# from cdhweb.blog.models import BlogPost
# from cdhweb.events.models import Event
# from cdhweb.projects.models import Project
from django.apps import apps
from django.conf import settings
from django.db import models
from django.template.defaultfilters import striptags, truncatechars_html
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import RichTextBlock, StreamBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

#: common features for paragraph text
PARAGRAPH_FEATURES = [
    'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul',
    'hr', 'blockquote', 'document', 'superscript', 'subscript',
    'strikethrough', 'code'
]


class BodyContentBlock(StreamBlock):
    '''Common set of blocks available in StreamFields for body text.'''
    paragraph = RichTextBlock(features=PARAGRAPH_FEATURES)
    image = ImageChooserBlock()
    document = DocumentChooserBlock()
    embed = EmbedBlock()
    #: used to hold content migrated from mezzanine via a "kitchen-sink"
    #: approach; virtually all html tags are allowed. should NOT be used when
    #: creating new pages.
    migrated = RichTextBlock(
        features=settings.RICHTEXT_ALLOWED_TAGS, icon="warning")


class PagePreviewDescriptionMixin(models.Model):
    '''Page mixin with logic for page preview content. Adds an optional
    richtext description field, and methods to get description and plain-text
    description, for use in previews on the site and plain-text metadata
    previews.'''

    # adapted from PPA; does not allow <p> tags in description
    #: brief description for preview display
    description = RichTextField(
        blank=True, features=['bold', 'italic'],
        help_text='Optional. Brief description for preview display. Will ' +
        'also be used for search description (without tags), if one is ' +
        'not entered.')
    #: maximum length for description to be displayed
    max_length = 225
    # (tags are omitted by subsetting default ALLOWED_TAGS)
    #: allowed tags for bleach html stripping in description
    allowed_tags = list((set(bleach.sanitizer.ALLOWED_TAGS) -
                         set(['a', 'blockquote'])))  # additional tags to remove

    class Meta:
        abstract = True

    def get_description(self):
        '''Get formatted description for preview. Uses description field
        if there is content, otherwise uses beginning of the body content.'''

        description = ''

        # use description field if set
        # use striptags to check for empty paragraph
        if striptags(self.description):
            description = self.description

        # if not, use beginning of body content
        else:
            # Iterate over blocks and use content from first paragraph content
            for block in self.body:
                if block.block_type == 'paragraph':
                    description = block
                    # stop after the first instead of using last
                    break

        description = bleach.clean(
            str(description),
            tags=self.allowed_tags,
            strip=True
        )
        # truncate either way
        return truncatechars_html(description, self.max_length)

    def get_plaintext_description(self):
        '''Get plain-text description for use in metadata. Uses
        search_description field if set; otherwise uses the result of
        :meth:`get_description` with tags stripped.'''

        if self.search_description.strip():
            return self.search_description
        return striptags(self.get_description())


class ContentPage(Page, PagePreviewDescriptionMixin):
    '''Basic content page model.'''

    #: main page text
    body = StreamField(BodyContentBlock, blank=True)

    # TODO attachments

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['HomePage', 'LandingPage', 'ContentPage']
    subpage_types = ['ContentPage']


class LandingPage(Page):
    '''Page type that aggregates and displays multiple :class:`ContentPage`s.'''

    #: short sentence overlaid on the header image
    tagline = models.CharField(max_length=255)
    #: image that will be used for the header
    header_image = models.ForeignKey('wagtailimages.image', null=True,
                                     blank=True, on_delete=models.SET_NULL, related_name='+')  # no reverse relationship
    #: main page text
    body = StreamField(BodyContentBlock, blank=True)

    search_fields = Page.search_fields + [index.SearchField('body')]
    content_panels = Page.content_panels + [
        FieldPanel('tagline'),
        StreamFieldPanel('body'),
        ImageChooserPanel('header_image'),
    ]

    parent_page_types = ['HomePage']
    subpage_types = ['ContentPage']


class PeopleLandingPage(LandingPage):
    """LandingPage subtype for People that holds ProfilePages."""
    parent_page_types = []  # can't be created in page editor
    subpage_types = ["people.ProfilePage"]


class HomePage(Page):
    '''A home page that aggregates and displays featured content.'''

    #: main page text
    body = StreamField(BodyContentBlock, blank=True)

    search_fields = Page.search_fields + [index.SearchField('body')]
    content_panels = Page.content_panels + [StreamFieldPanel('body')]

    parent_page_types = [Page]  # only root
    subpage_types = ['LandingPage', 'ContentPage']

    class Meta:
        verbose_name = 'Homepage'

    def get_context(self, request):
        '''Add featured updates, projects, and events to the page context.'''
        context = super().get_context(request)

        # FIXME an ImportError is thrown when classes in this module are
        # imported elsewhere if any of these three models are imported at the
        # top. Why?
        BlogPost = apps.get_model("blog", "blogpost")
        Project = apps.get_model("projects", "project")
        Event = apps.get_model("events", "event")

        # add up to 6 featured updates, otherwise use 3 most recent updates
        updates = BlogPost.objects.featured().published().recent()[:6]
        if not updates.exists():
            updates = BlogPost.objects.published().recent()[:3]
        context['updates'] = updates

        # add up to 4 highlighted, published projects
        projects = list(Project.objects.published().highlighted())
        shuffle(projects)
        context['projects'] = projects[:4]

        # add up to 3 upcoming, published events
        context['events'] = Event.objects.published().upcoming()[:3]

        return context
