from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from cdhweb.events.models import Event, EventType, Location

from django.template.defaultfilters import striptags


class EventAdmin(ThumbnailMixin, ModelAdmin):
    model = Event
    menu_icon = "date"
    list_display = (
        "admin_thumb",
        "title",
        "type",
        "speaker_list",
        "start_time",
        "end_time",
        "live",
    )
    list_display_add_buttons = "title"
    list_filter = ("start_time", "end_time", "type")
    list_export = (
        "title",
        "type",
        "start_time",
        "end_time",
        "location",
        "sponsor",
        "speaker_list",
        "attendance",
        "join_url",
        "content",
        "tags_",
        "updated",
    )
    export_filename = "cdhweb-events"
    search_fields = (
        "title",
        "speakers__person__first_name",
        "speakers__person__last_name",
        "body",
        "type__name",
        "sponsor",
        "location__name",
        "location__address",
    )
    thumb_image_field_name = "thumbnail"
    thumb_col_header_text = "thumbnail"
    ordering = ("-start_time",)
    list_per_page = 25

    def content(self, obj):
        # Plaintext body, named to match existing field
        return striptags(obj.body)

    def updated(self, obj):
        # Alias for last update, named to match existing field
        return obj.latest_revision_created_at

    def tags_(self, obj):
        # Transform tags into a spreadsheet-friendly form
        return ", ".join([t.name for t in obj.tags.all()])


class EventTypeAdmin(ModelAdmin):
    model = EventType
    menu_icon = "pick"
    list_display = ("name",)
    search_fields = ("name",)


class LocationAdmin(ModelAdmin):
    model = Location
    menu_icon = "site"
    list_display = ("name", "address", "short_name", "is_virtual")
    search_fields = ("short_name", "name", "address")


class EventsGroup(ModelAdminGroup):
    menu_label = "Events"
    menu_icon = "date"
    menu_order = 190
    items = (EventAdmin, EventTypeAdmin, LocationAdmin)


modeladmin_register(EventsGroup)
