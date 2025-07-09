from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from cdhweb.pages.models import RelatedLinkType
from cdhweb.people.models import Person, Profile, Title


class PersonAdmin(ThumbnailMixin, ModelAdmin):
    model = Person
    menu_icon = "group"
    list_display = (
        "admin_thumb",
        "first_name",
        "last_name",
        "current_title",
        "cdh_staff",
    )
    list_display_add_buttons = "first_name"
    search_fields = ("first_name", "last_name", "user__username")
    list_filter = ("pu_status", "cdh_staff")
    list_export = (
        "first_name",
        "last_name",
        "email",
        "most_recent_title",
        "department",
        "cdh_staff",
        "pu_status",
        "latest_grant",
        "profile_url",
    )
    list_per_page = 25
    export_filename = "cdhweb-people"
    thumb_image_field_name = "image"


class TitleAdmin(ModelAdmin):
    model = Title
    menu_icon = "order"
    list_display = ("title", "sort_order", "num_people")
    search_fields = ("title",)


class ProfileAdmin(ThumbnailMixin, ModelAdmin):
    model = Profile
    menu_icon = "user"
    list_display = ("admin_thumb", "title", "live")
    list_display_add_buttons = "title"
    list_filter = ("person__pu_status", "person__cdh_staff")
    list_per_page = 25
    search_fields = ("title", "body")
    ordering = ("title",)
    thumb_image_field_name = "image"
    exclude_from_explorer = True


class LinkTypeAdmin(ModelAdmin):
    model = RelatedLinkType
    menu_icon = "link"
    list_display = ("name", "sort_order")


class PeopleGroup(ModelAdminGroup):
    menu_label = "People"
    menu_icon = "group"
    menu_order = 200
    items = (PersonAdmin, TitleAdmin, ProfileAdmin, LinkTypeAdmin)


modeladmin_register(PeopleGroup)
