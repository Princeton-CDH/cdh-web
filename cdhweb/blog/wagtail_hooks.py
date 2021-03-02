from cdhweb.blog.models import BlogPost
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register


class BlogPostAdmin(ThumbnailMixin, ModelAdmin):
    model = BlogPost
    menu_icon = "edit"
    list_display = ("admin_thumb", "title",
                    "first_published_at", "live", "is_featured")
    list_display_add_buttons = "title"
    list_filter = ("is_featured", "first_published_at")
    list_export = ("title", "first_published_at", "is_featured",
                   "featured_image", "tags", "content")
    export_filename = "cdhweb-blogposts"
    search_fields = ("title", "content")
    exclude_from_explorer = True
    thumb_image_field_name = "featured_image"
    thumb_col_header_text = "image"
    list_per_page = 25
    menu_order = 210


modeladmin_register(BlogPostAdmin)