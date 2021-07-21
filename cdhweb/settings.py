import os

# List of allowed tags in the rich text editor (tinyMCE). We need to add the
# HTML5 <figcaption>, as it's not included by default.
#
RICHTEXT_ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'address', 'area', 'article',
    'aside', 'b', 'bdo', 'big', 'blockquote', 'br',
    'button', 'caption', 'center', 'cite', 'code', 'col',
    'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl',
    'dt', 'em', 'fieldset', 'figure', 'figcaption', 'font',
    'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'header', 'hr', 'i', 'img', 'input', 'ins', 'kbd',
    'label', 'legend', 'li', 'map', 'men', 'nav', 'ol',
    'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp',
    'section', 'select', 'small', 'span', 'strike',
    'strong', 'sub', 'sup', 'table', 'tbody', 'td',
    'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', '',
    'ul', 'var', 'wbr', 'iframe']

####################
# WAGTAIL SETTINGS #
####################

# Human-readable name of your Wagtail site shown on login to the Wagtail admin.
# https://docs.wagtail.io/en/latest/reference/settings.html#site-name
WAGTAIL_SITE_NAME = 'CDH Website'

# Tags are case-sensitive by default. In many cases the reverse is preferable.
# https://docs.wagtail.io/en/latest/reference/settings.html#case-insensitive-tags
TAGGIT_CASE_INSENSITIVE = True

# Shows where a particular image, document or snippet is being used on your site.
# Generates a query which may run slowly on sites with large numbers of pages.
# https://docs.wagtail.io/en/latest/reference/settings.html#usage-for-images-documents-and-snippets
WAGTAIL_USAGE_COUNT_ENABLED = True

# Use Wagtail's postgresql search backend.
# https://docs.wagtail.io/en/latest/reference/contrib/postgres_search.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.contrib.postgres_search.backend",
        "SEARCH_CONFIG": "english",
    },
}

# enable feature detection in images
WAGTAILIMAGES_FEATURE_DETECTION_ENABLED = True

# custom document model
WAGTAILDOCS_DOCUMENT_MODEL = "cdhpages.LocalAttachment"

# custom embed finders
WAGTAILEMBEDS_FINDERS = [
    {
        'class': 'wagtail.embeds.finders.oembed'
    },
    {
        'class': 'cdhweb.pages.embed_finders.GlitchHubEmbedFinder'
    },
]


########################
# MAIN DJANGO SETTINGS #
########################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
TIME_ZONE = 'America/New_York'

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# turn off internationalization for now
USE_I18N = False

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

# Supported languages
LANGUAGES = (
    ('en', 'English'),
)

# A boolean that turns on/off debug mode. When set to ``True``, stack traces
# are displayed for error pages. Should always be set to ``False`` in
# production. Best set to ``True`` in local_settings.py
DEBUG = False

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

# The numeric mode to set newly-uploaded files to. The value should be
# a mode you'd pass directly to os.chmod.
FILE_UPLOAD_PERMISSIONS = 0o644

# username for documenting database changes made by code
SCRIPT_USERNAME = 'script'

#############
# DATABASES #
#############

DATABASES = {
    "default": {
        # Add "postgresql", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.",
        # DB name or path to database file if using sqlite3.
        "NAME": "",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}


#########
# PATHS #
#########

# Full filesystem path to the project.
PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_APP

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'sitemedia'),
]

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

# Increase file upload size to roughly 50 MB
FILEBROWSER_MAX_UPLOAD_SIZE = 50000000

# Use local node-sass installed via npm
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'node_modules/node-sass/bin/node-sass {infile} {outfile}'),
)

# Use local postcss-cli and autoprefixer installed via npm
COMPRESS_AUTOPREFIXER_BINARY = 'node_modules/postcss-cli/bin/postcss'

COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    # NOTE: requires COMPRESS_ENABLED = True when DEBUG is True
    'django_compressor_autoprefixer.AutoprefixerFilter',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = "%s.urls" % PROJECT_APP

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_ROOT, "templates")
        ],
        "OPTIONS": {
            'loaders': [
                'apptemplates.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.tz",
                # 'wagtail.contrib.settings.context_processors.settings',
                # 'wagtailmenus.context_processors.wagtailmenus',
                'cdhweb.context_extras',
                'cdhweb.context_processors.template_settings',
                'cdhweb.pages.context_processors.page_intro',
            ],
        },
    },
]

################
# APPLICATIONS #
################

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    # required to avoid https://github.com/wagtail/wagtail/issues/1824
    'wagtail.contrib.search_promotions',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.postgres_search',
    'wagtail.core',
    'wagtailmenus',
    'modelcluster',
    'taggit',
    'adminsortable2',
    "compressor",
    "fullurl",
    "django_cas_ng",
    "pucas",
    # local apps
    "cdhweb.projects",
    "cdhweb.people",
    "cdhweb.events",
    "cdhweb.blog",
    'cdhweb.pages',
]

# List of middleware classes to use. Order is important; in the request phase,
# these middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    # Uncomment if using internationalisation or localisation
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

# pucas configuration that is not expected to change across deploys
# and does not reference local server configurations or fields
PUCAS_LDAP = {
    # attributes expected by init_profile_from_ldap method
    'ATTRIBUTES': [
        'uid', 'universityid', 'pustatus', 'ou', 'givenName',
        'sn', 'mail', 'telephoneNumber', 'street', 'title', 'displayName'],

    'ATTRIBUTE_MAP': {
        'first_name': 'givenName',
        'last_name': 'sn',
        'email': 'mail',
    },
    # local method to populate profile fields based on available
    # ldap information
    'EXTRA_USER_INIT': 'cdhweb.people.models.init_person_from_ldap'
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# Support embedding content from Princeton's Media Central (Kaltura MediaSpace)
# See https://knowledge.kaltura.com/help/mediaspace-oembed-integration
media_central_provider = {
    "endpoint": "https://mediacentral.princeton.edu/oembed",
    "urls": (
        r"^https://mediacentral\.princeton\.edu/id/(?:\w+)\?width=\d+&height=\d+&playerId=\d+$",
        r"^https://mediacentral\.princeton\.edu/media/[^/]+/(?:\w+)$"
    )
}

# These will be tried in order; we put the Media Central one first so that the
# custom provider will be used. See:
# https://docs.wagtail.io/en/stable/advanced_topics/embeds.html#customising-the-provider-list
WAGTAILEMBEDS_FINDERS = [
    {
        'class': 'wagtail.embeds.finders.oembed',
        'providers': [media_central_provider],
    },
    {
        'class': 'wagtail.embeds.finders.oembed',
    },
    {
        'class': 'cdhweb.pages.embed_finders.GlitchHubEmbedFinder'
    },
]


#########################
# OPTIONAL APPLICATIONS #
#########################


try:
    # django-debug-toolbar
    # https://django-debug-toolbar.readthedocs.io/en/latest/
    import debug_toolbar
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
except ImportError:
    pass

try:
    # django-extensions
    # https://django-extensions.readthedocs.io/en/latest/
    import django_extensions
    INSTALLED_APPS.append("django_extensions")
except ImportError:
    pass

try:
    # django-dbml
    # https://github.com/makecodes/django-dbml
    import django_dbml
    INSTALLED_APPS.append("django_dbml")
except ImportError:
    pass

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local_settings import *", we use exec so that
# local_settings has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.

f = os.path.join(PROJECT_APP_PATH, "local_settings.py")
if os.path.exists(f):
    import sys
    import imp
    module_name = "%s.local_settings" % PROJECT_APP
    module = imp.new_module(module_name)
    module.__file__ = f
    sys.modules[module_name] = module
    exec(open(f, "rb").read())
