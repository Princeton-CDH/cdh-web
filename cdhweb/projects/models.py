import itertools

from django import forms
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page, PageManager, PageQuerySet
from wagtail.search import index
from wagtailautocomplete.edit_handlers import AutocompletePanel

from cdhweb.pages.blocks.accordion_block import ProjectAccordion
from cdhweb.pages.mixin import OpenGraphMixin, StandardHeroMixin
from cdhweb.pages.models import BasePage, DateRange, LandingPage, LinkPage, RelatedLink
from cdhweb.people.models import Person


class ProjectQuerySet(PageQuerySet):
    def _current_grant_query(self):
        """QuerySet filter to find projects with a current grant,
        based on start date before current date and end date after current
        date or not set.
        """
        today = timezone.now()
        return models.Q(grants__start_date__lt=today) & (
            models.Q(grants__end_date__gt=today)
            | models.Q(grants__end_date__isnull=True)
        )

    def current(self):
        """Projects with a current grant, based on dates"""
        return self.filter(self._current_grant_query()).distinct()

    def not_current(self):
        """Projects with no current grant, based on dates"""
        return self.exclude(self._current_grant_query())

    #: grant types that indicate staff or postdoc project
    staff_postdoc_grants = [
        "Staff R&D",
        "Staff Project",
        "Postdoctoral Research Project",
    ]

    def staff_or_postdoc(self):
        """Staff and postdoc projects, based on grant type"""
        return self.filter(
            grants__grant_type__grant_type__in=self.staff_postdoc_grants
        ).exclude(working_group=True)

    def not_staff_or_postdoc(self):
        """Exclude staff and postdoc projects, based on grant type"""
        return self.exclude(
            grants__grant_type__grant_type__in=self.staff_postdoc_grants
        ).exclude(working_group=True)

    def working_groups(self):
        """Include only projects with the working group flag set"""
        return self.filter(working_group=True)

    def order_by_newest_grant(self):
        """order by grant start date, most recent grants first; secondary
        sort by project title"""
        # NOTE: using annotation to get just the most recent start date
        # to avoid issues with projects appearing multiple times.
        return self.annotate(last_start=models.Max("grants__start_date")).order_by(
            "-last_start", "title"
        )

    def recent(self):
        """Order projects by date published."""
        return self.order_by("-first_published_at")


# custom manager for wagtail pages, see:
# https://docs.wagtail.io/en/stable/topics/pages.html#custom-page-managers
ProjectManager = PageManager.from_queryset(ProjectQuerySet)


class Project(BasePage, OpenGraphMixin, ClusterableModel, StandardHeroMixin):
    """Page type for a CDH sponsored project or working group."""

    template = "projects/project_page.html"

    accordion = StreamField(
        [("accordion", ProjectAccordion(label="Project Accordion"))],
        use_json_field=True,
        blank=True,
        verbose_name="Project Details",
        max_num=1,
    )

    project_website = models.URLField(
        verbose_name="Project Website",
        null=True,
        blank=True,
        help_text="Project website URL.",
    )

    cdh_built = models.BooleanField(
        "CDH Built",
        default=False,
        help_text="Project built by CDH Development & Design team.",
    )
    working_group = models.BooleanField(
        "Working Group",
        default=False,
        help_text="Project is a long-term collaborative group associated with the CDH.",
    )

    members = models.ManyToManyField(
        Person, through="Membership", related_name="members"
    )

    method = ParentalManyToManyField(
        "ProjectMethod",
        related_name="projects",
        blank=True,
    )

    field = ParentalManyToManyField(
        "ProjectField",
        related_name="projects",
        blank=True,
    )
    role = ParentalManyToManyField(
        "ProjectRole",
        related_name="projects",
        blank=True,
    )

    # TODO attachments (#245)

    # can only be created underneath project landing page
    parent_page_types = [
        "projects.ProjectsLandingPageArchived",
        "projects.ProjectsLandingPage",
    ]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = StandardHeroMixin.content_panels + [
        FieldRowPanel(
            (
                FieldPanel("cdh_built"),
                FieldPanel("working_group"),
            ),
            "Settings",
        ),
        FieldPanel("accordion"),
        FieldPanel("body"),
        FieldPanel("project_website"),
        FieldRowPanel(
            [
                FieldPanel("method", widget=forms.CheckboxSelectMultiple),
                FieldPanel("field", widget=forms.CheckboxSelectMultiple),
                FieldPanel("role", widget=forms.CheckboxSelectMultiple),
            ],
            "Filter fields",
        ),
        InlinePanel("related_links", label="Links"),
        InlinePanel(
            "grants",
            panels=[
                FieldRowPanel((FieldPanel("start_date"), FieldPanel("end_date"))),
                FieldPanel("grant_type"),
            ],
            label="Grants",
        ),
        InlinePanel(
            "memberships",
            panels=[
                FieldRowPanel((FieldPanel("start_date"), FieldPanel("end_date"))),
                AutocompletePanel("person"),
                FieldPanel("role"),
            ],
            label="Members",
        ),
        FieldPanel("attachments"),
    ]
    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("short_title"),
                FieldPanel("short_description"),
                FieldPanel("feed_image"),
            ],
            "Share Page",
        ),
    ] + BasePage.promote_panels

    # custom manager/queryset logic
    objects = ProjectManager()

    # search fields
    search_fields = StandardHeroMixin.search_fields + [
        index.SearchField("body"),
        index.FilterField("cdh_built"),
        index.FilterField("path"),
        index.FilterField("depth"),
        index.FilterField("method"),
        index.FilterField("field"),
        index.FilterField("role"),
        # We can't actually filter on these right now, but leave them here in case we can somedays
        # See: https://docs.wagtail.org/en/v5.2.5/topics/search/indexing.html#filtering-on-index-relatedfields
        index.RelatedFields(
            "grants", [index.FilterField("start_date"), index.FilterField("end_date")]
        ),
        index.RelatedFields(
            "members",
            [
                index.SearchField("first_name"),
                index.SearchField("last_name"),
            ],
        ),
    ]

    def __str__(self):
        return self.title

    @property
    def website_url(self):
        """URL for this Project's website, if set"""
        website = self.related_links.filter(type__name="Website").first()
        if self.project_website:
            return self.project_website
        elif website:
            return website.url

    def latest_grant(self):
        """Most recent :class:`Grant` for this Project"""
        if self.grants.count():
            return self.grants.order_by("-start_date").first()

    def current_memberships(self):
        """:class:`MembershipQueryset` of current members sorted by role"""
        # NOTE memberships is a FakeQuerySet from modelcluster.ParentalKey when
        # the page is being previewed in wagtail, so Q lookups are not possible.
        # see: https://github.com/wagtail/django-modelcluster/issues/121
        memberships = Membership.objects.filter(project__pk=self.pk)
        # uses memberships rather than members so that we can retain role
        # information attached to the membership
        today = timezone.now().date()
        # if the last grant for this project is over, display the team
        # for that grant period
        latest_grant = self.latest_grant()
        if latest_grant and latest_grant.end_date and latest_grant.end_date < today:
            return memberships.filter(start_date__lte=latest_grant.end_date).filter(
                models.Q(end_date__gte=latest_grant.start_date)
                | models.Q(end_date__isnull=True)
            )

        # otherwise, return current members based on date
        return memberships.filter(start_date__lte=today).filter(
            models.Q(end_date__gte=today) | models.Q(end_date__isnull=True)
        )

    def alums(self):
        """:class:`PersonQueryset` of past members sorted by last name"""
        # uses people rather than memberships so that we can use distinct()
        # to ensure people aren't counted multiple times for each grant
        # and because we don't care about role (always 'alum')
        return (
            self.members.distinct()
            .exclude(membership__in=self.current_memberships())
            .order_by("last_name")
        )

    def get_sitemap_urls(self, request):
        """Override sitemap to prioritize projects built by CDH with a website."""
        # output is a list of dict; there should only ever be one element. see:
        # https://docs.wagtail.io/en/stable/reference/contrib/sitemaps.html#urls
        urls = super().get_sitemap_urls(request=request)
        if self.website_url and self.cdh_built:
            urls[0]["priority"] = 0.7
        elif self.website_url or self.cdh_built:
            urls[0]["priority"] = 0.6
        return urls

    def display_tags(self):
        """
        Get role, method and field values as tag-y objects

        The method/field/role fields are used for filtering
        the projects in the search, but CDH have also
        requested that they be shown the same way tags are
        for many other types of object -- This function
        delivers them in a (template-equivalent) manner so
        they can be displayed
        """
        return sorted(
            str(t)
            for t in itertools.chain(
                self.method.all(),
                self.field.all(),
            )
        )


class GrantType(models.Model):
    """Model to track kinds of grants"""

    grant_type = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.grant_type


class Grant(index.Indexed, DateRange):
    """A specific grant associated with a project"""

    project = ParentalKey(Project, on_delete=models.CASCADE, related_name="grants")
    grant_type = models.ForeignKey(GrantType, on_delete=models.CASCADE)

    class Meta:
        ordering = ["start_date", "project"]

    def __str__(self):
        return "%s: %s (%s)" % (
            self.project.title,
            self.grant_type.grant_type,
            self.years,
        )

    search_fields = [
        index.FilterField("start_date"),
        index.FilterField("end_date"),
    ]


class Role(models.Model):
    """A role on a project"""

    title = models.CharField(max_length=255, unique=True)
    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title

    def __lt__(self, other):
        # NOTE we need to order Memberships using role sort order by default,
        # but modelcluster doesn't support ordering via related lookups, so
        # we can't order by role__sort_order on Membership. Instead we do this.
        # see: https://github.com/wagtail/django-modelcluster/issues/45
        return self.sort_order < other.sort_order


class Membership(DateRange):
    """Project membership - joins project, user, and role."""

    project = ParentalKey(Project, on_delete=models.CASCADE, related_name="memberships")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        ordering = ("role", "person")

    # admin edit configuration
    panels = [
        FieldRowPanel((FieldPanel("start_date"), FieldPanel("end_date")), "Dates"),
        FieldPanel("person"),
        FieldPanel("role"),
        FieldPanel("project"),
    ]

    def __str__(self):
        return "%s - %s on %s (%s)" % (self.person, self.role, self.project, self.years)


class ProjectRelatedLink(RelatedLink):
    """Through-model for associating projects with relatedlinks"""

    project = ParentalKey(
        Project, on_delete=models.CASCADE, related_name="related_links"
    )

    def __str__(self):
        return "%s – %s (%s)" % (self.project, self.type, self.display_url)


class ProjectsLandingPageArchived(LandingPage):
    """Container page that defines where Project pages can be created."""

    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is a Project; this is so that
    # Projects made in the admin automatically are created here.
    subpage_types = [Project, LinkPage]
    # use the regular landing page template
    template = LandingPage.template


class ProjectsLandingPage(StandardHeroMixin, Page):
    featured_project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.SET_NULL
    )

    content_panels = StandardHeroMixin.content_panels + [FieldPanel("featured_project")]

    search_fields = StandardHeroMixin.search_fields

    settings_panels = Page.settings_panels

    subpage_types = [Project]

    def get_child_queryset(self, request, filter_form):
        # Sometimes we pass the empty form, which isn't cleanable
        clean_filters = getattr(filter_form, "cleaned_data", {})
        query_string = clean_filters.pop("q", None)

        # It's not currently possible to filter by
        # RelatedFields, so because current-ness is part of
        # Grants we need to apply this later, defaults True
        current_filter = clean_filters.pop("current", True)

        # Use a Project queryset so we can apply type-specific filters
        children = Project.objects.child_of(self).public().live()

        # We've engineered the remaining filter options to
        # map *directly* to Project columns and only apply
        # the ones with a value
        to_apply = {k: v for k, v in clean_filters.items() if v}
        children = children.filter(**to_apply)

        if query_string:
            children = children.search(query_string).get_queryset()

        if current_filter:
            # The "current" filter uses relations to
            # `Grant`s, which aren't able to be filtered
            # using the Wagtail search backend, as they're
            # too nested. To dodge this, we instead uses the
            # existing method on the objects Manager, after
            # making the results into a queryset (above)
            children = children.current()

        children = children.order_by("title")
        return children

    def get_context(self, request, year=None, month=None):
        from cdhweb.projects.forms import ProjectFiltersForm

        context = super().get_context(request)
        form_args = request.GET.dict()
        if form_args:
            form = ProjectFiltersForm(form_args)
        else:
            form = ProjectFiltersForm()

        form.is_valid()
        child_queryset = self.get_child_queryset(request, form)

        # Exclude featured_project from the results, and add
        # it to the context note this means the template
        # should access `featured_project` *NOT*
        # `self.featured_project`
        if (
            self.featured_project
            and child_queryset.filter(id=self.featured_project_id).exists()
        ):
            context["featured_project"] = self.featured_project
            child_queryset = child_queryset.exclude(pk=self.featured_project.pk)

        child_queryset = child_queryset.prefetch_related(
            "members", "method", "field", "role", "hero_image", "hero_image__renditions"
        )

        context["results"] = child_queryset
        context["filter_form"] = form

        return context


class ProjectMethod(models.Model):
    """
    Model for project methodologies/approaches

    Used for the projects filter
    """

    method = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.method


class ProjectField(models.Model):
    """
    Model for project Fields

    Used for the projects filter
    """

    field = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.field


class ProjectRole(models.Model):
    """
    Model for project roles

    Used for the projects filter
    """

    role = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.role
