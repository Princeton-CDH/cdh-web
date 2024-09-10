from django.conf import settings
from django.templatetags.static import static
from wagtail.models import Site

from cdhweb.pages.utils import get_default_preview_img_url


def template_settings(request):
    """Template context processor: add selected setting to context
    so it can be used on any page ."""

    feature_flags = getattr(settings, "FEATURE_FLAGS", [])

    context_extras = {
        "SHOW_TEST_WARNING": getattr(settings, "SHOW_TEST_WARNING", False),
        "site": Site.find_for_request(request),
        "default_preview_image": get_default_preview_img_url(),
        # Include analytics based on settings.DEBUG or override in settings.py
        # Defaults to opposite of settings.DEBUG
        "INCLUDE_ANALYTICS": getattr(settings, "INCLUDE_ANALYTICS", not settings.DEBUG),
        "GTAGS_ANALYTICS_ID": getattr(
            settings, "GTAGS_ANALYTICS_ID", not settings.DEBUG
        ),
        "PLAUSIBLE_ANALYTICS_SCRIPT": getattr(
            settings, "PLAUSIBLE_ANALYTICS_SCRIPT", not settings.DEBUG
        ),
        "PLAUSIBLE_ANALYTICS_404s": getattr(
            settings, "PLAUSIBLE_ANALYTICS_404s", not settings.DEBUG
        ),
        # pass any feature flags that are configured
        "FEATURE_FLAGS": feature_flags,
        "FAVICON": favicon_path(),
    }
    return context_extras


def favicon_path():
    """Determine which favicon to use based on any feature flags and test warning.
    Returns full local path, including static url.
    """
    icon_version = "favicon.ico"
    # use test favicon when test warning is enabled as another visual indicator
    if getattr(settings, "SHOW_TEST_WARNING", False):
        icon_version = "favicon-test.ico"

    return static(icon_version)


def show_test_warning(request):
    return {"SHOW_TEST_WARNING": getattr(settings, "SHOW_TEST_WARNING", False)}
