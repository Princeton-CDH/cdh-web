CHANGELOG
=========

4.0.1
-----
- bugfix: `Title` related positions should be optional when creating new titles
- Add support for Plausible analytics; configurable with ``PLAUSIBLE_ANALYTICS_SCRIPT``
  and ``PLAUSIBLE_ANALYTICS_404s = True``
- Accessibility fixes

4.0.0
-----
- Major overhaul, redesigned and rebuilt by Springload 
  - Dropped custom views and shift logic to using wagtail pages throughout
  - numerous new wagtail blocks added
  - frontend build now uses webpack, dropped django compressor

3.5.3
-----

- Upgrade to wagtail 5.2 (LTS)
- Use django-split-settings to manage application settings

3.5.2
-----

Configure django-compressor to use content hash so css urls will be the same for load-balanced servers.

3.5.1
-----

Maintenance release: npm package updates

3.5
---

- As a content editor, I want to search for people by name when adding them to projects, events, or setting tem as blog post authors, so that I can easily lookup the correct person.
- As a content editor, I want an option to add formatted code to blog posts or other content pages, so I can share technical content clearly.
- update 404 and 500 error page images
- bugfix: project thumbnails not displaying on project card if project doesn't have a larger image associated

3.4.5
-----
- updated to django 4.2 and wagtail 5.0
- updated to python 3.8+ (tested against 3.8-3.11)
- updated node version 18
- removed editoria11y v1 integration
- removed Percy visual testing workflow

3.4.4
-----

* bugfix: website link isn't available on person list pages if person has an unpublished profile page

3.4.3
-----

* Update to include Humanities + Data Science Institute instructors and participants as
affiliates and student affiliates
* bugfixes:
  * correct Event ordering on semester archive pages
  * fix search fields for Events in wagtail interface (solves 500 error)
  * correct RDFa structure for event speakers with URLs
* accessibility:
  * fix semantic heading hierarchy problem on project and event detail pages


3.4.2
-----

* bugfix: improve display for event cards with more than 3 speakers
* bugfix: persist larger upload file size limit setting

3.4.1
-----

* bugfix: Event cards showing up out of order on the homepage and upcoming events


3.4
---

* As a user, I want to search across all pages by keyword so I can find specific content that interests me.
* As a user, I want to access the site search via the main navigation so I can start a search from anywhere.
* As a user, I want basic information about the CDH displayed on the homepage so that I can learn about the CDH and read more about its values.
* bugfix: Can't add someone to current staff if they have any exec committee position, whether current or not


3.3.1
-----

* Add optional purple mode, which can be enabled in settings

3.3
---

* As a Content Editor, I want existing page links to resolve after I rename or move a page so that I don't have to manually create a redirect.
* As an Editor, I want to see accessibility checks when I'm logged in or previewing a page so that I will be alerted if something is causing accessibility problems and have guidance about how to fix it.
* Support embedding Media Central content via oEmbed
* bugfix: Embed sizing ignores container margins on mobile
* chore: set up visual regression testing
* chore: set up black and isort pre-commit hooks

3.2
---

* As a content editor, I want to embed external content in editorial and other pages, so that I can include dynamic content.
* bugfix: Unset email for people displays as "none" on profile pages


3.1
---

* As a User, I want to see CDH Data Fellows listed on the Affiliates and Students pages so I know who received a fellowship.
* bugfix: search description is not used as fallback for description

3.0.3
-----

* bugfix: short description for blog posts are not editable in wagtail

3.0.2
-----

* bugfix: make django admin accessible for management of users, redirects, etc.
* chore: remove mezzanine and all associated code
* chore: upgrade django and wagtail

3.0.1
-----

* bugfix: fix template path to avoid error when previewing blog post
* bugfix: fix error when adding multiple speakers to an event (modelcluster sort)
* bugfix: ensure page models (blog post, event, project, profile) are ordered, including in admin
* bugfix: display _recently_ published featured blogposts on the homepage
* bugfix: fix unique slug error when publishing a new blog post without saving a draft
* chore: remove temporary models, model fields, and all exodus migration code
* Adds a one-time custom manage command to clean up migrated html content

3.0
---

* As a moderator, I want to create and edit events in wagtail so that I can manage them just like other pages.
* As a moderator, I want to create and edit people in wagtail so that I can manage them just like pages.
* As an editor, I want to create and edit blog posts in wagtail so that I can take advantage of its editing capabilities.
* As an editor, I want upload and manage page attachments in wagtail so that I can associate them with pages.
* As an editor, I want existing attachments migrated to wagtail so that I can manage them in the new system.
* As a moderator, I want existing content pages migrated from mezzanine to wagtail so that I can manage them in the new system.
* As a moderator, I want existing uploaded images migrated to wagtail so that I can manage them in the new system.
* As a moderator, I want existing related links migrated to wagtail so that I can manage them in the new system.
* As an editor, I want existing blog posts migrated to wagtail so that I can manage them in the new system.
* As a moderator, I want existing projects migrated to wagtail so that I can manage them in the new system.
* As a moderator, I want existing events migrated to wagtail so that I can manage them in the new system.
* As a moderator, I want existing people migrated to wagtail so that I can manage them in the new system.
* As a moderator, I want People automatically organized into person list pages so I don't have to manually manage these pages.
* As a moderator, I want Projects automatically organized into list pages so I don't have to manually manage these pages.
* As a moderator, I want Events automatically organized by upcoming events and by semester, so that I don't have to manually manage these list pages.
* As a moderator, I want blog posts automatically listed by latest posts, by month, and by year so that I don't have to manually manage these pages.
* As a search engine, I want a sitemap of all pages on the CDH site so that I can index them for users to search.
* As an editor, I want to manage the menus displayed across the site in wagtail so that I can easily update them when needed.
* As an admin, I want to see the edit history for a page, including edits before the wagtail migration, so that I can see the history of edits to a page.
* chore: add apache rewrite rule to ansible for migrated media
* chore: Include DB diagrams in documentation
* chore: remove inactive user accounts
* chore: clean image EXIF metadata
* bugfix: superuser permissions required for editing content due to mezzanine site permissions
* bugfix: meta information for project pages is incorrect
* bugfix: Some past student profiles are displaying twice
* bugfix: slug logic doesn't ensure uniqueness
* bugfix: 500 error when trying to view admin blog post list if not superuser
* bugfix: working groups display on main project page


2.8.1
-----

* Switch database backend from MySQL to PostgreSQL
* Continuous integration now uses GitHub Actions instead of Travis-CI

2.8
---

* As an admin, I want to associate project contributors with projects based on the dates they were involved instead of by grant, so that I can accurately reflect project team membership over time.
* As an admin, I want to create staff projects that aren't R&D and have them show up on the Staff Projects page so I can highlight new work like Startwords.
* As a user, I want to learn about the DH Working Groups sponsored by the CDH so that I can get involved with a group that matches my interests.
* As a user, I want to see PGRA profiles listed with students and postdoc profiles listed with staff, so I understand how these people relate to the CDH.
* bugfix: project admin edit pages load slowly, especially for large projects
* bugfix: affiliate grant year ranges on profile list pages are incorrect
* chore: shift CI to github actions
* chore: rename master -> main

2.7
---

* As an admin, I want to add a virtual location to events so that people know they can join remotely.
* show staff affiliates on affiliates page
* bugfix: project alums display incorrectly lists members of most recent grant
* bugfix: blog post links not inside ``<div>`` don't get link style
* chore: upgrade django & mezzanine
* chore: remove pa11y-ci

2.6
---

* As a Content Editor, I want a visual indicator when I'm viewing a page that is not yet published so that I can distinguish between published and unpublished content.
* As a Content Editor, I want to add text content to the events page so that I can add context to the list of events.
* display grant history on project pages
* add a 'status override' flag to always show grant memberships as current or past
* add a template for embedding the event cosponsorship form
* add a visual indicator when viewing a draft page
* bugfix: second-level navigation pages don't respect "show in nav" setting
* bugfix: links in lists don't get body link style
* chore: adjust content priority values in sitemap
* accessibility: make main navigation usable with a keyboard
* accessibility: make "skip to" links visible when focused via keyboard
* accessibility: add text-shadow to landing page headings
* accessibility: add empty alt for event featured images
* accessibility: add link titles for event cards

2.5
---

* bugfix: event card doesn't display names from person, only from profile
* Document installation and use of timezone files for MariaDB/MySQL
* Update social media links
* Add links to profile urls for project alums


2.4.3
-----

* bugfix: blogpost RSS feed does not respect draft status
* Configure admin search fields for projects, grants, and blog posts
* Display event attendance in admin list view

2.4.2
-----

* Order faculty affiliates by last name
* Use png instead of svg for social media / opengraph preview icon images,
  since svg is not supported
* Tweak profile card display logic for faculty fellowship
* Include Postgraduate Research Assistants on the postdocs page
* Configure admin search for position list
* Use book icon for reading group, location marker for travel grants

2.4.1
-----

* bugfix: blog post list author and event detail speaker link to unpublished
  profiles
* Require Pillow v 5.2
* Style fix for h2 padding on project and event cards

2.4
---

Accessibility updates and new features to display projects in different groupings
with indicators for projects build by CDH and those with live websites, and
multiple pages to display current and past people affiliated with CDH.

This release includes numerous design fixes and improvements.

Features
~~~~~~~~
* As a user, I want to easily read and use the main site navigation so I can get to the content that interests me.
* As a user, I want to traverse the main navigation using a keyboard so that I can access site content more easily.
* As a user, I want to see current, staff, and past projects so I can easily see which projects are active and know more about staff research.
* As a user, I want to see which projects were developed by CDH so that I can get a better sense of CDH involvement in the projects.
* As a user, I want to see which projects in the project list have a live website so that I can see which projects are accessible and get to them.
* As a user, I want to easily find project URLs so I can get to the actual websites and see projects that are live.
* As a user, I want to see CDH staff, postdocs, and students on separate pages so I can see current and past people associated with CDH grouped by category.
* As a user, I want to see photos and brief details for faculty affiliates and executive committee members so I can see the faces of people associated with CDH.
* As a user, I want to see upcoming and past speakers at CDH events so I can see what kind of scholars CDH is bringing to campus.
* As a user, I want to see recent blog posts by a CDH staff member or other affiliate on their profile page so that I can read more about their work.
* As a user, I want to easily find the subscribe link so I know there is a newsletter and how to subscribe to it.
* As an admin, I want to edit text content on the home page so that I can manage and update brief introductory content for site visitors.
* As a content admin, I want to add and edit text to be included on people pages so that I can describe faculty affiliation or other groups.
* As a content admin, I want to document event attendance in the database so that it can be tracked and reported with other event information.

Chores, fixes, and other items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* bugfix: HTML entity rendering issues for blog post and page preview text
* bugfix: home page carousel now respects draft status
* Embedded consultation request form on user-editable page
* Customize XML Sitemap with last modification dates for all content
* Display phone number and office location on profile detail page
* Use CDH icons for related page attachment cards and open graph/twitter previews
* Set up automated accessibility testing with pa11y-ci
* Removed data import script written for migration from CDH web 1.0
* Upgraded to Mezzanine 4.3

2.3.1
-----

Sets a null href attribute on carousel links to prevent reloading the page but keep them accessible to screen readers.

2.3
---

* As a Content Editor, I want my rich text editor preview to match the way the content will display on the site so that I don't have to check the published version myself.
* As a Content Editor, I should only be able to use supported formatting and tags when I edit site content so that the CDH has a uniform web presence.
* As a Content Editor, I want to designate blog posts as featured so I can highlight their importance.
* As a user, I want to see featured updates on the homepage so I can see what's going on at the CDH.

Upgrade tinyMCE to v4.7.9.

2.2.2
-----

Downgrade Django to 1.10.x (and latest released version of Mezzanine)
to avoid a Django compatibility issue with filebrowser_safe.

2.2.1
-----

Minor Sphinx documentation and README cleanup.

2.2
---

* As a user, I want to see past CDH positions on a staff member profile page so I can learn about a person's history with CDH.
* As a user I want to view a list of alumni so I can get learn about people who have worked with CDH in the past.
* As a user, I want to see details about CDH alumni so I can learn about their past work at CDH and where they are now.
* Upcoming events page now includes 6 most recent past events
* Upgrade to Django 1.11.x
* bug fix: home page doesn't display any message when there are no upcoming events
* bug fix: events page is broken when there are no upcoming events
* bug fix: events with different starting and ending months error on display
* bug fix: non-CDH address display on event detail page repeats information
* bug fix: allow adding speakers to events pages without creating a profile
* bug fix: people with multiple positions are listed multiple times on the staff page
* Multiple design fixes and improvements'

  * converted from Neat grid to CSS Grid for main grid and footer
  * fixed broken image reference for events with no detail image
  * mobile footer formatting and mobile main navigation menu
  * Typography link style fixes
  * Main menu navigation (LM viewport) now provides submenu links on hover
  * Improved navigation menu style for moving between events pages, staff and alumni pages
  * Improvements to event card, project detail page, profile page, content pages

2.1
---

* As a content editor, I want to associate people with projects more efficiently so I don't have to enter repeating information.
* bug fix: Resource links on user profile page don't work
* bug fix: People with multiple positions are listed multiple times on the staff page
* bug fix: Event urls now honor year/month and event slugs can be repeated
* Basic twitter/opengraph metadata now included in page headers
* robots.txt now managed by the application; includes path to sitemap.xml
* favicon now managed by the application; includes dev/test icon
* Many improvements and clean up in design implementation

2.0
---

**CDH web 2.0 is a completely new implementation of the functionality in the
previous version, with a restructured database and site templates based on
bourbon+neat rather than bootstrap.**

Profiles
~~~~~~~~

* As a user I want to view a list of staff members so I can get an idea of the people who work at the CDH.
* As a user, I want to see details about a staff member so I can learn about their role, research interests, and how to contact them.
* As an admin, I want to create and edit staff profiles so I can publish information about staff research and roles.
* As an admin, I want user information and titles automatically populated so I don't have to manually enter it.

Events
~~~~~~

* As a user I want to view a list of upcoming events so that I can find and attend events that interest me.
* As a user, I want to view event details so I can decide if I'm interested and know when and where to attend.
* As a user, I want to view previous events by semester so that I can get a sense of event and workshop offerings.
* As a user, I want to download event information as ical so I can add it to my personal calendar.
* As a content editor, I want to create and edit event types so I can categorize kinds of events.
* As a content editor, I want to create and edit event locations so that I can enter them once and have them displayed consistently across the site.
* As a content editor, I want to create and edit events so that I can publicize workshops, lectures, or other events.

Projects
~~~~~~~~

* As a user I want to see a list of current projects so I can learn more about the work of CDH.
* As a user, I want to view sponsored project details so I can read about project goals, progress, and contributors.
* As an admin, I want to associate urls for other resources with projects so that I can provide links to materials related to projects.
* As an admin, I want to create and edit project roles and associate people as members of projects so that I can document project contributors.
* As an admin, I want to create and edit grant types and associate grants with projects, so that I can document when and which kinds of grants a project received from CDH.
* As an admin user, I want to create and edit project pages so that I can publish information about sponsored projects.

Blog
~~~~

* As a user, I want to view previous blog posts by year and month so that I can read past updates.
* As a user, I want to subscribe to a blog post feed so I can read CDH updates in the feed reader of my choosing.
* As a user, I want to view blog posts so that I can read updates about CDH and its work.
* As a user, I want to browse a paginated list of blog posts so that I can find and read older updates about CDH and its work.
* As a content editor, I want to create and edit blog posts so that I can share updates about CDH and its work.
* As a content editor, I want to associate an author other than myself with a blog post so that I can indicate who wrote the content.
* As a content editor, I want to associate one or more authors with a blog post so that I can document everyone who contributed to the content.

Other Content
~~~~~~~~~~~~~

* As a user, I want to navigate using the header or footer menus, so that I can find the content I'm looking for.
* As a user I want to view upcoming events and highlighted projects on the homepage so I can get a sense of the CDH and its activities.
* As a user, I want to view content pages so that I can read materials that interest me.
* As a user, I want to view and download files associated with pages on the site so that I can access other materials related to the content.
* As an admin, I want to upload files and media and associate them with other content so that I can share files and other non-web content with users.
* As an admin I want to edit and create resource types so I can determine what kind of links and resources can be associated with people and projects.
* As an admin, I want to manage links in the header so that I can update navigation when the site changes.
* As an admin, I want to create and manage landing pages and other content pages so that I can publish top-level and other content pages.
* As an admin, I want to manage links in the footer so I can update site navigation when content changes.

Import
~~~~~~
* As an admin, I want an import of content from the previous version of the site so that all the information available on the old site is migrated to the new version.
