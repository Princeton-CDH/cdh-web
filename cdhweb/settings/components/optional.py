"""Optional apps: add to INSTALLED_APPS when they are installed."""

from cdhweb.settings.components.base import INSTALLED_APPS, MIDDLEWARE

INTERNAL_IPS = [
    "127.0.0.1",
]

try:
    # django-debug-toolbar
    # https://django-debug-toolbar.readthedocs.io/en/latest/
    import debug_toolbar
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

    # django-extensions
    # https://django-extensions.readthedocs.io/en/latest/
    import django_extensions
    INSTALLED_APPS.append("django_extensions")

    # django-dbml
    # https://github.com/makecodes/django-dbml
    import django_dbml
    INSTALLED_APPS.append("django_dbml")

except ImportError:
    pass
