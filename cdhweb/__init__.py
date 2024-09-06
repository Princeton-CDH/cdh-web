__version__ = "4.0.0"


# context processor to add version to the template environment; can be
# manually overridden in the project's settings
def context_extras(request):
    from django.conf import settings

    return {"SW_VERSION": getattr(settings, "SW_VERSION", __version__)}
