from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from cdhweb.projects.models import (
    GrantType,
    Membership,
    Project,
    ProjectField,
    ProjectMethod,
    Role,
)


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
        "description",
        "body",
        "website_url",
        "last_published_at",
    )
    search_fields = ("title", "description", "body")
    export_filename = "cdhweb-projects"
    thumb_image_field_name = "thumbnail"
    thumb_col_header_text = "thumbnail"
    ordering = ("title",)


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
    )


modeladmin_register(ProjectsGroup)
