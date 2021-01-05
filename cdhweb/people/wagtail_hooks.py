from cdhweb.people.models import Person, ProfilePage, Title
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup,
                                                modeladmin_register)


class PersonAdmin(ThumbnailMixin, ModelAdmin):
    model = Person
    menu_icon = "group"
    list_display = ("first_name", "last_name", "admin_thumb", "current_title",
                    "cdh_staff")
    search_fields = ("first_name", "last_name", "user__username")
    list_filter = ("pu_status", "cdh_staff")
    list_export = ("first_name", "last_name", "admin_thumb", "current_title",
                   "cdh_staff")
    export_filename = "cdhweb-people"
    thumb_image_field_name = "image"


class TitleAdmin(ModelAdmin):
    model = Title
    menu_icon = "order"
    list_display = ("title", "sort_order", "num_people")
    search_fields = ("title",)

# remove ProfilePages from the regular wagtail page editor and create a special
# admin area for them underneath the "people" section


class ProfilePageAdmin(ThumbnailMixin, ModelAdmin):
    model = ProfilePage
    menu_icon = "user"
    list_display = ("title", "admin_thumb", "live")
    search_fields = ("title",)
    thumb_image_field_name = "image"
    exclude_from_explorer = True


class PeopleGroup(ModelAdminGroup):
    menu_label = "People"
    menu_icon = "group"
    menu_order = 200
    items = (PersonAdmin, TitleAdmin, ProfilePageAdmin)


# TODO inlines for editing PersonRelatedLinks (#181) on People
modeladmin_register(PeopleGroup)
