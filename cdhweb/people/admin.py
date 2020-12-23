from django.contrib import admin
from mezzanine.core.admin import DisplayableAdmin

from cdhweb.people.models import Title, Person, Profile, Position
from cdhweb.resources.models import PersonResource


class TitleAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "num_people")
    list_editable = ("sort_order",)


class PositionInline(admin.TabularInline):
    model = Position


class PersonResourceInline(admin.TabularInline):
    model = PersonResource


class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "current_title", "cdh_staff")
    # NOTE: if we switched to profile instead of person here, is_staff
    # and published could be made list editable
    fields = ("user__username", "first_name", "last_name", "email")

    inlines = [PositionInline, PersonResourceInline]

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.profile.tags.all())
    tag_list.short_description = "Tags"

    # use inline fields for titles and resources
    # also: suppress management/auth fields like password, username, permissions,
    # last login and date joined


class ProfileAdmin(DisplayableAdmin):
    list_display = ("title", "status", "is_staff", "pu_status", "admin_link",
                    "admin_thumb")
    list_filter = ("status", "is_staff", "pu_status")
    search_fields = ("title", "user__last_name", "user__username",
                     "user__first_name", "bio")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("attachments", )
    # customized fieldset based on DisplayableAdmin field set
    fieldsets = (
        (None, {
            "fields": ["user", "title", "pu_status", "is_staff", "education",
                       "bio", "phone_number", "office_location",
                       "job_title", "department", "institution",
                       "image", "thumb",
                       "status", ("publish_date", "expiry_date"),
                       "attachments"],
        }),
        ("Page Metadata", {
            "fields": ["_meta_title", "slug",
                       ("description", "gen_description"),
                       "keywords", "in_sitemap"],
            "classes": ("collapse-open",)
        }),
    )


class PositionAdmin(admin.ModelAdmin):
    list_display = ("person", "title", "start_date", "end_date")
    date_hierarchy = "start_date"
    search_fields = ("person__user__username", "person__first_name", "person__last_name",
                     "title__title", "start_date", "end_date")


admin.site.register(Title, TitleAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Position, PositionAdmin)
