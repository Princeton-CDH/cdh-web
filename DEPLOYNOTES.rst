Deploy Notes
============

3.3
---

- After deployment, the Wagtail search index should be populated::

    python manage.py update_index

  This command only needs to be run once, since signals will take care of any
  indexing after the initial run.


3.0.2
-----

- This release reset migrations without mezzanine dependencies. Updating
  requires the following steps:

  1. Clear out django migration history for old migrations::

      python manage.py dbshell
      delete from django_migrations;

  2. Fake the new migrations::

      python manage.py migrate --fake

- Automated deployments will fail if the above steps are not followed when
  migrating. To avoid this problem, use ansible's step mode::

      ansible-playbook cdh-web_qa.yml --step

  When you reach the migration step, do not execute migrations (N) and instead
  manually follow the steps above on the target machine via ssh. You can then
  choose the "continue" (c) option to finish the rest of the playbook normally.


3.0.1
-----

- After deploy, run a script to clean up markup in migrated content from the 
exodus script in the last release::

  python manage.py cleanup_migrated_content

3.0
---

- After deployment, the main exodus script should be run to move content from
  mezzanine to wagtail with `python manage.py exodus`.

2.8.1
-----

- Data will need to be migrated out of the existing database and into a Postgres
  database. The `pgloader` tool can be used for this purpose.

2.8
---

- The "Postdocs" list page has been removed, so its corresponding page should be
  deleted in Mezzanine.
- A new "DH Working Groups" page should be created under the Projects page in
  mezzanine with its slug set to `/projects/working-groups` to enable the new
  DH Working Groups page.
- Any Working Groups that were created as pages (not projects) can be deleted,
  and their content can be moved into a new Project.
- Any Working Groups that were assigned the "working group" grant type can have
  this removed, and the grant type can be deleted.
- Any non-R&D Staff Projects that were assigned the "staff r&d" grant type can
  have this changed to "Staff Projects", and the grant type can be deleted.

2.7
---

- The "Faculty Affiliates" page has changed to show both Faculty and Staff, and
  thus its title and content should be updated accordingly in Mezzanine.
- The django-compressor build process may fail on nodejs versions <10. Ensure
  that v10 is installed and available on the target machine.


2.6
---

- Adds a cosponsorship request form embed template similar to the consult form.
  A `RichTextPage` needs to be created with its url set to `/events/cosponsor`
  in order to automatically embed the form.
- The events page needs to be recreated as a `RichTextPage` to support adding
  text at the top of the page. To disable the text at the top, enter two non-
  breaking spaces in the text field. Make sure the url remains `/events`.

2.2
---

- Adds an alumni page, parallel to current staff.  Existing profile pages
  for past staff should be republished.
- Fixes rich text page template to include page title as an H1.  Existing
  content with the title repeated will need to be edited.

2.1
---

- Resource names have been changed to store proper case in the database.
  Existing installations should update the three pre-populated items manually.
- Update local settings to turn on Google Analytics.

2.0
---

- Update default site in Django admin to match deployed site url
- Initialize admin and other users with createcasuser before running
  the data import.
- Import data from the previous version of the site (exported via Django
  dumpdata) using `python manage.py import_datav1 path_to_data.json`
