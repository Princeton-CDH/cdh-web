from django.db.models.base import Model
from cdhweb.people.models import Person, Position, Profile, Title
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup,
                                                modeladmin_register)


class PersonAdmin(ThumbnailMixin, ModelAdmin):
    model = Person
    menu_icon = "group"
    list_display = ("admin_thumb", "first_name", "last_name", "current_title",
                    "cdh_staff")
    search_fields = ("first_name", "last_name", "user__username")
    list_filter = ("pu_status", "cdh_staff")
    thumb_image_field_name = "image"


class TitleAdmin(ModelAdmin):
    model = Title
    menu_icon = "order"
    list_display = ("title", "sort_order", "num_people")
    search_fields = ("title",)

class PeopleGroup(ModelAdminGroup):
    menu_label = "People"
    menu_icon = "group"
    menu_order = 200
    items = (PersonAdmin, TitleAdmin)

# TODO inlines for editing PersonRelatedLinks (#181) on People
# TODO ProfilePage admin


modeladmin_register(PeopleGroup)
