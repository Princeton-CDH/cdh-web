from copy import deepcopy
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.admin import (DisplayableAdmin, OwnableAdmin,
                                  BaseTranslationModelAdmin)
from mezzanine.conf import settings
from mezzanine.twitter.admin import TweetableAdminMixin

from .models import  BlogPost


class BlogPostAdmin(TweetableAdminMixin, DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    list_display = ["title", "author_list", "status", "admin_link", "tag_list",
        "admin_thumb"]
    list_editable = ("status",)
    list_filter = ("status", )
    date_hierarchy = "publish_date"
    radio_fields = {"status": admin.HORIZONTAL}
    # filter_horizontal = ("categories", "related_posts",)
    filter_horizontal = ("related_posts",)

    prepopulated_fields = {"slug": ("title",)}
    # based on Displayable fieldset
    fieldsets = (
        (None, {
            "fields": ["title", "status", ("publish_date", "expiry_date"),
                       "content", "featured_image", "users", "tags"]
        }),
        (_("Meta data"), {
            "fields": ["_meta_title", "slug",
                       ("description", "gen_description"),
                        "keywords", "in_sitemap"],
            "classes": ("collapse-closed",)
        }),
        (_("Other posts"), {
            "classes": ("collapse-closed",),
            "fields": ("related_posts",),
        }),
    )

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        # OwnableAdmin.save_form(self, request, form, change)
        # NOTE: ownable automatically sets owner to current user, not
        # sure that behavior makes sense for us
        return DisplayableAdmin.save_form(self, request, form, change)

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    def get_changeform_initial_data(self, request):
        # default author to current user
        return {'users': [request.user]}


admin.site.register(BlogPost, BlogPostAdmin)
