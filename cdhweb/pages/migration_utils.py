import json
import logging
from datetime import datetime

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase

logger = logging.getLogger('wagtail.core')

# see for an explanation of django-treebeard & the `path` attribute:
# http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
def get_parent(apps, page):
    '''Find the parent of a wagtail page instance. Always returns the underlying
    :class:`wagtail.core.models.Page` rather than a subclass.'''

    # if the path is 4 digits, we're at the root, so there is no parent
    if len(page.path) == 4:
        return None

    # otherwise remove the final 4 digits to get the parent's id (pk)
    Page = apps.get_model('wagtailcore', 'Page')
    return Page.objects.get(path=page.path[:-4])

# add_child utility method adapted from:
# http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
# see also:
# https://github.com/wagtail/wagtail/blob/stable/2.3.x/wagtail/core/models.py#L442
def add_child(apps, parent_page, klass, **kwargs):
    '''Create a new draft wagtail page of type klass as a child of page instance
    parent_page, passing along kwargs to its create() function.'''

    # add/set the correct content type for the new page
    ContentType = apps.get_model('contenttypes.ContentType')
    page_content_type = ContentType.objects.get_or_create(
        model=klass.__name__.lower(),
        app_label=klass._meta.app_label,
    )[0]

    # create the new page
    page = klass.objects.create(
        content_type=page_content_type,
        path='%s%04d' % (parent_page.path, parent_page.numchild + 1),
        depth=parent_page.depth + 1,
        numchild=0,
        live=False,  # create as a draft so that URL is set correctly on publish
        **kwargs
    )

    # update the parent's child count
    parent_page.numchild += 1
    parent_page.save()

    # log the creation and return the page
    logger.info(
        "Page created: \"%s\" id=%d content_type=%s.%s path=%s",
        page.title,
        page.id,
        klass._meta.app_label,
        klass.__name__,
        page.url_path
    )

    return page


def page_to_dict(page):
    return {
        'pk': page.pk,
        'live': page.live,
        'slug': page.slug,
        'path': page.path,
        'title': page.title,
        'depth': page.depth,
        'owner': page.owner,
        'locked': page.locked,
        'expired': page.expired,
        'numchild': page.numchild,
        'url_path': page.url_path,
        'expire_at': page.expire_at,
        'seo_title': page.seo_title,
        'go_live_at': page.go_live_at,
        'draft_title': page.draft_title,
        'content_type': page.content_type,
        'show_in_menus': page.show_in_menus,
        'live_revision': page.live_revision,
        'last_published_at': page.last_published_at,
        'search_description': page.search_description,
        'first_published_at': page.first_published_at,
        'has_unpublished_changes': page.has_unpublished_changes,
        'latest_revision_created_at': page.latest_revision_created_at,
    }

# adapted from wagtail's `save_revision`:
# https://github.com/wagtail/wagtail/blob/stable/2.3.x/wagtail/core/models.py#L631
def create_revision(apps, page, user=None, created_at=datetime.now(), **kwargs):
    '''Add a :class:`wagtail.core.models.PageRevision` to document changes to a
    Page associated with a particular user and timestamp.'''

    PageRevision = apps.get_model('wagtailcore', 'PageRevision')

    # serialize the page's current state and apply changes from kwargs
    content = page_to_dict(page)
    for (key, value) in kwargs.items():
        try:
            page[key] = value 
            content[key] = value
        except (KeyError, AttributeError):
            continue

    # create the revision object
    revision = PageRevision.create(
        content_json=json.dumps(content),
        user=user,
        submitted_for_moderation=False,
        approved_go_live_at=None,
        created_at=created_at
    )

    # update and save the page
    page.latest_revision_created_at = created_at
    page.draft_title = page.title
    page.has_unpublished_changes = True

    # log the revision and return it
    logger.info("Page edited: \"%s\" id=%d revision_id=%d", page.title,
                page.id, revision.id)

    return revision

# adapted from `TestMigrations`
# https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
# and from winthrop-django
class TestMigrations(TestCase):

    app = None
    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)
        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass
