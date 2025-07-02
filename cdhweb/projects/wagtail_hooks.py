import csv

from django.http import HttpResponse
from django.template.defaultfilters import striptags
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem
from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from cdhweb.pages.blocks.accordion_block import ProjectAccordion
from cdhweb.projects.models import (
    GrantType,
    Membership,
    Project,
    ProjectField,
    ProjectMethod,
    ProjectRole,
    Role,
)


class ProjectAccordionCSVeMenuItem(ActionMenuItem):
    name = "action-accordion-csv"
    label = "Export Accordion to CSV"

    def get_url(self, context):
        page = context.get("page")
        if page and isinstance(page, Project):
            return reverse("export_project_accordion_csv", kwargs={"page_id": page.id})
        return None


@hooks.register("construct_page_action_menu")
def setup_accordion_export_menu_items(menu_items, request, context):
    page = context.get("page")
    if page and isinstance(page, Project):
        menu_items.extend(
            [
                ProjectAccordionCSVeMenuItem(order=10),
            ]
        )


@hooks.register("register_admin_urls")
def register_accordion_export_url():
    """Register the accordion export URL"""
    from .views import export_project_accordion_csv_view

    return [
        path(
            "pages/<int:page_id>/export-accordion-csv/",
            export_project_accordion_csv_view,
            name="export_project_accordion_csv",
        ),
    ]


class ProjectAdmin(ThumbnailMixin, ModelAdmin):
    model = Project
    menu_label = "Projects"
    menu_icon = "site"
    list_display = ("admin_thumb", "title", "live", "cdh_built")
    list_display_add_buttons = "title"
    list_filter = ("grants__grant_type",)
    list_export = (
        "title",
        "working_group",
        "cdh_built",
        "tags",
        "page_summary",
        "page_content",
        "website_url",
        "last_published_at",
    )
    search_fields = ("title", "description", "body")
    export_filename = "cdhweb-projects"
    thumb_image_field_name = "thumbnail"
    thumb_col_header_text = "thumbnail"
    ordering = ("title",)

    def tags(self, obj):
        """
        Generate text tags like we got prior to v4
        """
        return obj.display_tags()

    # Supply plaintext versions of these -- named to
    # maintain the existing spreadsheet field header (from
    # verbose_names)
    def page_summary(self, obj):
        return striptags(obj.description)

    def page_content(self, obj):
        return striptags(obj.body)


class MembershipAdmin(ModelAdmin):
    model = Membership
    menu_icon = "group"
    list_display = ("start_date", "end_date", "person", "role", "project")
    list_filter = ("start_date", "end_date")
    list_export = ("start_date", "end_date", "person", "role", "project")
    search_fields = (
        "project__title",
        "role__title",
        "person__first_name",
        "person__last_name",
    )
    export_filename = "cdhweb-memberships"
    ordering = ("-start_date",)


class GrantTypeAdmin(ModelAdmin):
    model = GrantType
    menu_icon = "pick"
    list_display = ("grant_type",)
    search_fields = ("grant_type",)


class RoleAdmin(ModelAdmin):
    model = Role
    menu_icon = "order"
    list_display = ("title", "sort_order")
    list_editable = ("title", "sort_order")
    search_fields = ("title",)


class ProjectMethodAdmin(ModelAdmin):
    model = ProjectMethod
    menu_icon = "arrow-right"
    list_display = ["method"]
    list_editable = ["method"]
    search_fields = ["method"]


class ProjectFieldAdmin(ModelAdmin):
    model = ProjectField
    menu_icon = "arrow-right"
    list_display = ["field"]
    list_editable = ["field"]
    search_fields = ["field"]


class ProjectRoleAdmin(ModelAdmin):
    model = ProjectRole
    menu_icon = "arrow-right"
    list_display = ["role"]
    list_editable = ["role"]
    search_fields = ["role"]


class ProjectsGroup(ModelAdminGroup):
    menu_label = "Projects"
    menu_icon = "site"
    menu_order = 210
    items = (
        ProjectAdmin,
        MembershipAdmin,
        RoleAdmin,
        GrantTypeAdmin,
        ProjectMethodAdmin,
        ProjectFieldAdmin,
        ProjectRoleAdmin,
    )


modeladmin_register(ProjectsGroup)
