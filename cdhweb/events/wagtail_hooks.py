from cdhweb.events.models import Event, EventType, Location
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup,
                                                modeladmin_register)


class EventAdmin(ThumbnailMixin, ModelAdmin):
    model = Event
    menu_icon = "date"
    list_display = ("admin_thumb", "title", "type", "speaker_list",
                    "start_time", "end_time", "live")
    list_display_add_buttons = "title"
    list_filter = ("start_time", "end_time", "type")
    list_export = ("title", "type", "start_time", "end_time", "location", "sponsor",
                   "speaker_list", "attendance", "join_url", "content", "tags", "updated")
    export_filename = "cdhweb-events"
    search_fields = ("title", "speakers__person__first_name",
                     "speakers__person__last_name", "content", "type", 
                     "sponsor", "location")
    exclude_from_explorer = True
    thumb_image_field_name = "thumbnail"
    thumb_col_header_text = "thumbnail"
    list_per_page = 25


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
