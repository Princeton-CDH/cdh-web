from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mezzanine.core.admin import DisplayableAdmin, DisplayableAdminForm
from adminsortable2.admin import SortableAdminMixin

from .models import Title, Profile, Position, Person
from cdhweb.resources.models import UserResource


class TitleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'num_people')
    # NOTE: could make title list-editable, but then we need something
    # to be the edit link
    # list_display = ('sort_order', 'title', )
    # list_editable = ('title',)

    # FIXME: there is an incompatibility with SortableAdminMixin templates
    # and/or css/js includes and grappelli; sorting works fine when
    # grappelli is not installed.  We should be able to address this
    # with a little bit of template customization.



class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    form = DisplayableAdminForm
    # NOTE: may not be able to use displayable admin with inline;
    # could still use DisplayableAdminForm
    prepopulated_fields = {"slug": ("title",)}
    # TODO: grapelli templates don't include a way to have the first profile
    # default to open instead of collapsed; maybe use javascript
    # classes = ("collapse-open",)
    # inline_classes = ('collapse-open',)  # this is ignored
    exclude = ('tags', )


class PositionInline(admin.TabularInline):
    model = Position


class UserResourceInline(admin.TabularInline):
    model = UserResource


class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'current_title',
        'tag_list')
    fields = ('first_name', 'last_name', 'email')
    inlines = [ProfileInline, PositionInline, UserResourceInline]

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.profile.tags.all())
    tag_list.short_description = 'Tags'


    # use inline fields for titles and resources
    # also: suppress management/auth fields like password, username, permissions,
    # last login and date joined


class PositionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'start_date', 'end_date')
    date_hierarchy = 'start_date'


admin.site.register(Title, TitleAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Position, PositionAdmin)