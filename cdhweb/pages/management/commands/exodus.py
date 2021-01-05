"""Convert mezzanine-based pages to wagtail page models."""
import filecmp
import glob
import json
import os
import os.path
import shutil
from collections import defaultdict

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db.models import Q
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.pages import models as mezz_page_models
from wagtail.core.blocks import RichTextBlock
from wagtail.core.models import Page, Site, Collection, get_root_collection_id
from wagtail.images.models import Image

from cdhweb.pages.models import ContentPage, HomePage, LandingPage, PeopleLandingPage
from cdhweb.people.models import Person, Profile, ProfilePage


class Command(BaseCommand):
    help = __file__.__doc__

    # list to track migrated mezzanine pages by pk
    migrated = []

    def convert_slug(self, slug):
        """Convert a Mezzanine slug into a Wagtail slug."""
        # wagtail stores only the final portion of a URL with no slashes
        # remove trailing slash, then return final portion without slashes
        return slug.rstrip("/").split("/")[-1]

    def create_homepage(self, page):
        """Create and return a Wagtail homepage based on a Mezzanine page."""
        return HomePage(
            title=page.title,
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "migrated",
                "value": page.richtextpage.content,   # access via richtextpage
            }]),
            search_description=page.description,    # store even if generated
        )

    def create_landingpage(self, page):
        """Create and return a Wagtail landing page based on a Mezzanine page."""
        return LandingPage(
            title=page.title,
            tagline=page.landingpage.tagline,   # landing pages have a tagline
            header_image=self.get_wagtail_image(page.landingpage.image),
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "migrated",
                "value": page.landingpage.content,
            }]),
            search_description=page.description,    # store even if generated
            # TODO not dealing with images yet
            # TODO not setting menu placement yet
            # TODO search keywords?
        )

    def create_contentpage(self, page):
        """Create and return a Wagtail content page based on a Mezzanine page."""
        return ContentPage(
            title=page.title,
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "migrated",
                # access via richtextpage when present
                "value": page.richtextpage.content if hasattr(page, "richtextpage") else "",
            }]),
            search_description=page.description,    # store even if generated
            # TODO not dealing with images yet
            # TODO not setting menu placement yet
            # NOTE: not migrating search keywords
            # TODO set the correct visibility status
            # NOTE not login-restricting pages since we don't use it
            # NOTE not setting expiry date; handled manually
            # NOTE inclusion in sitemap being handled by sitemap itself
            # NOTE set has_unpublished_changes on page?
        )

    def handle(self, *args, **options):
        """Create Wagtail pages for all extant Mezzanine pages."""
        # clear out wagtail pages and revisions for idempotency
        Page.objects.filter(depth__gt=2).delete()
        # PageRevision.objects.all().delete()

        # convert media images to wagtail images
        self.image_exodus()

        # populate person images
        self.person_image_exodus()

        # create the new homepage
        try:
            old_homepage = mezz_page_models.Page.objects.get(slug="/")
            homepage = self.create_homepage(old_homepage)
            # mark home page as migrated
            self.migrated.append(old_homepage.pk)
        # in some situations (e.g. fixture loading) there's no homepage
        except mezz_page_models.Page.DoesNotExist:
            old_homepage = None
            homepage = HomePage(
                title="The Center for Digital Humanities at Princeton",
                seo_title="The Center for Digital Humanities at Princeton",
                slug="",
            )
        root = Page.objects.get(depth=1)
        root.add_child(instance=homepage)
        root.save()

        # point the default site at the new homepage and delete any others.
        # if they are deleted prior to switching site.root_page, the site will
        # also be deleted in a cascade, which we don't want
        site = Site.objects.get()
        site.root_page = homepage
        site.save()
        Page.objects.filter(depth=2).exclude(pk=homepage.pk).delete()

        # create a dummy top-level projects/ page for project pages to go under
        if mezz_page_models.Page.objects.filter(slug="projects").exists():
            projects = ContentPage(
                title="Sponsored Projects",
                slug="projects",
                seo_title="Sponsored Projects",
            )
            homepage.add_child(instance=projects)
            homepage.save()
            self.migrated.append(
                mezz_page_models.Page.objects.get(slug='projects').pk)
        else:
            projects = None

        # create a dummy top-level events/ page for event pages to go under
        if mezz_page_models.Page.objects.filter(slug="events").exists():
            events = ContentPage(
                title="Events",
                slug="events",
                seo_title="Events"
            )
            homepage.add_child(instance=events)
            homepage.save()
            # mark events content page as migrated
            self.migrated.append(
                mezz_page_models.Page.objects.get(slug='events').pk)
        else:
            events = None

        # manually migrate the top-level people/ page to a special subtype
        try:
            old_people = mezz_page_models.Page.objects.get(slug="people")
            people = PeopleLandingPage(
                title=old_people.title,
                tagline=old_people.landingpage.tagline,
                header_image=self.get_wagtail_image(old_people.landingpage.image),
                slug=self.convert_slug(old_people.slug),
                seo_title=old_people._meta_title or old_people.title,
                body=json.dumps([{
                    "type": "migrated",
                    "value": old_people.landingpage.content,
                }]),
                search_description=old_people.description,
            )
            homepage.add_child(instance=people)
            homepage.save()
            # mark as migrated
            self.migrated.append(old_people.pk)
        except mezz_page_models.Page.DoesNotExist:
            people = None

        # migrate children of homepage
        if old_homepage:
            for page in old_homepage.children.all():
                self.migrate_pages(page, homepage)

        # special cases
        # - migrate event pages but specify new events page as parent
        if events:
            event_pages = mezz_page_models.Page.objects \
                .filter(Q(slug__startswith="events/") | Q(slug="year-of-data"))
            for page in event_pages:
                self.migrate_pages(page, events)

        if projects:
            # - migrate project pages but specify new projects list page as parent
            # - process about page last so project pages don't nest
            project_pages = mezz_page_models.Page.objects \
                .filter(slug__startswith="projects/").order_by('-slug')
            for page in project_pages:
                self.migrate_pages(page, projects)

        # migrate people pages but use new landingpage subtype as parent
        # TODO create new PersonListPage subtypes
        if people:
            people_pages = mezz_page_models.Page.objects \
                .filter(slug__startswith="people/").order_by('-slug')
            for page in people_pages:
                self.migrate_pages(page, people)

        # migrate all remaining pages, starting with pages with no parent
        # (i.e., top level pages)
        for page in mezz_page_models.Page.objects.filter(parent__isnull=True):
            self.migrate_pages(page, homepage)

        # special cases — consult/co-sponsor form
        self.form_pages()

        # profile pages
        self.profile_pages()

        # report on unmigrated pages
        unmigrated = mezz_page_models.Page.objects.exclude(
            pk__in=self.migrated)
        print('%d unmigrated mezzanine pages:' % unmigrated.count())
        for page in unmigrated:
            print('\t%s — slug/url %s)' % (page, page.slug))

        # delete mezzanine pages here? (but keep for testing migration)

    def migrate_pages(self, page, parent):
        """Recursively convert a mezzanine page and all its descendants
        to Wagtail pages with the same hierarchy.

        :params page: mezzanine page to convert
        :params parent: wagtail page the new page should be added to
        """

        # if a page has already been migrated, skip it
        if page.pk in self.migrated:
            return

        # create the new version of the page according to page type
        if hasattr(page, "landingpage"):
            new_page = self.create_landingpage(page)
        else:
            # treat everything else as page / richtexpage
            if hasattr(page, "link"):
                print('WARN: converting link page to content page %s ' % (page))
            new_page = self.create_contentpage(page)

        parent.add_child(instance=new_page)
        parent.save()

        # set publication status
        if page.status != CONTENT_STATUS_PUBLISHED:
            new_page.unpublish()

        # add to list of migrated pages
        self.migrated.append(page.pk)

        # recursively create and add new versions of all this page's children
        for child in page.children.all():
            self.migrate_pages(child, new_page)

    def form_pages(self):
        # migrate embedded google forms from mezzanine templates
        # add new migrated to body with iframe from engage/consult template and save
        # set a height on the iframe to ensure it renders correctly
        if ContentPage.objects.filter(slug="consult").exists():
            consults = ContentPage.objects.get(slug="consult")
            consults.body = json.dumps([
                {"type": "migrated", "value": consults.body[0].value.source},
                {"type": "migrated", "value": '<iframe title="Consultation Request Form" height="2400" src="https://docs.google.com/forms/d/e/1FAIpQLScerpyeQAgp91Iy66c1rKbKSwbSpeuB5yHh14l3G9C86eUjsA/viewform?embedded=true">Loading...</iframe>'}
            ])
            consults.save()
        # # do the same for cosponsorship page
        if ContentPage.objects.filter(slug="cosponsor").exists():
            cosponsor = ContentPage.objects.get(slug="cosponsor")
            cosponsor.body = json.dumps([
                {"type": "migrated", "value": cosponsor.body[0].value.source},
                {"type": "migrated", "value": '<iframe title="Cosponsorship Request Form" height="3250" src="https://docs.google.com/forms/d/e/1FAIpQLSeP40DBM7n8GYgW_i99nRxY5T5P39DrIWyIwq9LggIwu4r5jQ/viewform?embedded=true">Loading...</iframe>'}
            ])
            cosponsor.save()

    # cached collections used for migrated media
    collections = {
        # get root collection so we can add children to it
        'root': Collection.objects.get(pk=get_root_collection_id())
    }

    def profile_pages(self):
        """Exodize all existing Profiles to new ProfilePage model."""
        # all the fields on Profile that moved to Person will have been handled
        # by django migrations; we just need to create new Page models
        people_landing = PeopleLandingPage.objects.first()
        if not people_landing:
            return
        for profile in Profile.objects.filter(user__person__isnull=False):
            # NOTE not sure why Profile.user.person fails; works in console?
            person = Person.objects.get(user=profile.user)
            profile_page = ProfilePage(
                person=person,
                title=profile.title,
                image=self.get_wagtail_image(profile.image) if profile.image else None,
                education=profile.education,
                bio=json.dumps([
                    {"type": "migrated", "value": profile.bio},
                ])
            )
            # added as child of people landing page so slugs are correct
            people_landing.add_child(instance=profile_page)
            people_landing.save()
            # if the old profile wasn't published, unpublish the new one
            if profile.status != CONTENT_STATUS_PUBLISHED:
                profile_page.unpublish()

    def get_collection(self, name):
        # if we don't already have this collection, get it
        if name not in self.collections:
            # try to get it if it already exists
            coll = Collection.objects.filter(name=name).first()
            # otherwise, create it
            if not coll:
                coll = Collection(name=name)
                self.collections['root'].add_child(instance=coll)
                self.collections['root'].save()

            self.collections[name] = coll

        return self.collections[name]

    def image_exodus(self):
        # generate wagtail images for all uploaded media

        # mezzanine/filebrowser_safe doesn't seem to have useful objects
        # or track metadata, so just import from the filesystem

        # delete all images and collections prior to run
        # (clear out past migration attempts)
        Image.objects.all().delete()
        # Collection.objects.exclude(pk=get_root_collection_id()).delete()
        # fix collection tree so root collection is up to date
        # FIXME: this is still not working; seems to error on alternate runs
        # Collection.fix_tree()

        # also delete any wagtail image files, since they are not deleted
        # by removing the objects
        shutil.rmtree('%s/images' % settings.MEDIA_ROOT, ignore_errors=True)
        shutil.rmtree('%s/original_images' %
                      settings.MEDIA_ROOT, ignore_errors=True)

        # get media filenames to migrate, with duplicates filtered out
        media_filenames = self.get_media_files()

        for imgpath in media_filenames:
            extension = os.path.splitext(imgpath)[1]
            # skip unsupported files based on file extension
            # NOTE: leaving this here in case we want to handle
            # documents the same way
            if extension in ['.pdf', '.svg', '.docx']:
                continue

            # if image is in a subdirectory under uploads (e.g. projects, blog)
            # add it to a collection with that name
            relative_path = os.path.dirname(imgpath) \
                .replace('%s/uploads/' % settings.MEDIA_ROOT, '')

            # there are two variants of Slavic DH, one with and one
            # without a space; remove the space so they'll be in one collection
            basedir = relative_path.split('/')[0].replace(' ', '')
            collection = None
            if basedir:
                collection = self.get_collection(basedir)

            with open(imgpath, 'rb') as imgfilehandle:
                title = os.path.basename(imgpath)
                # passing collection=None errors, so
                # only specify collection option when we have one
                extra_opts = {}
                if collection:
                    extra_opts['collection'] = collection
                try:
                    Image.objects.create(
                        title=title,
                        file=ImageFile(imgfilehandle, name=title),
                        **extra_opts)
                except Exception as err:
                    # seems to mean that height/width calculation failed
                    # (usually non-images)
                    print('Error creating image for %s: %s' % (imgpath, err))

    def get_media_files(self):
        # wagtail images support: GIF, JPEG, PNG, WEBP
        imgfile_path = '%s/**/*.*' % settings.MEDIA_ROOT
        # get filenames for all uploaded files
        filenames = glob.glob(imgfile_path, recursive=True)
        # aggregate files by basename to identify files with the same
        # name in different locations
        unique_filenames = defaultdict(list)
        for path in filenames:
            unique_filenames[os.path.basename(path)].append(path)

        # check files with the same name in multiple locations
        for key, val in unique_filenames.items():
            if len(val) > 1:
                samefile = filecmp.cmp(val[0], val[1], shallow=False)
                # if the files are the same
                if samefile:
                    # keep the first one and remove the others from the
                    # list of files to be migrated
                    extra_copies = val[1:]

                # if not all the same, identify the largest
                # (all are variant/cropped versions of the same image)
                else:
                    largest_file = None
                    largest_size = 0
                    for filepath in val:
                        size = os.stat(filepath).st_size
                        if size > largest_size:
                            largest_size = size
                            largest_file = filepath

                    extra_copies = [f for f in val if f != largest_file]

                # remove duplicate and variant images that
                # will not be imported into wagtail
                for extra_copy in extra_copies:
                    filenames.remove(extra_copy)

        return filenames

    def get_wagtail_image(self, image):
        # get the migrated wagtail image for a foreign-key image
        # using image file basename, which is migrated as image title
        try:
            return Image.objects.get(title=os.path.basename(image.name))
        except Image.DoesNotExist as err:
            print("Error locating image %s: %s" % (image, err))
            return None

    def person_image_exodus(self):
        # for people with profile, set larger image as wagtail image for person
        for profile in Profile.objects.filter(user__person__isnull=False):
            # NOTE not sure why Profile.user.person fails; works in console?
            person = Person.objects.get(user=profile.user)
            if profile.image:
                person.image = self.get_wagtail_image(profile.image)
                person.save()
