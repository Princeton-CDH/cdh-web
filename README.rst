CDH Website
===========

.. sphinx-start-marker-do-not-remove

.. image:: https://github.com/Princeton-CDH/cdh-web/workflows/unit%20tests/badge.svg
   :target: https://github.com/Princeton-CDH/cdh-web/actions?query=workflow%3A%22unit+tests%22
   :alt: Unit test status

.. image:: https://codecov.io/gh/Princeton-CDH/cdh-web/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/Princeton-CDH/cdh-web
   :alt: Code coverage

.. image:: https://github.com/Princeton-CDH/cdh-web/workflows/dbdocs/badge.svg
    :target: https://dbdocs.io/princetoncdh/cdhweb
    :alt: dbdocs build

.. image:: https://percy.io/static/images/percy-badge.svg
    :target: https://percy.io/3201ecb4/cdh-web
    :alt: Visual regression tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: "code style Black"

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/
    :alt: "imports: isort"

Python 3.11 / Django 4.2 / Node 18 / PostgreSQL 12
`cdhweb` is a Django+Wagtail application that powers the CDH website
with custom models for people, events, and projects.

View `software and architecture documentation <https://princeton-cdh.github.io/cdh-web/>`_
for the current release.

This repository uses `git-flow <https://github.com/nvie/gitflow>`_ conventions; **main**
contains the most recent release, and work in progress will be on the **develop** branch.
Pull requests should be made against **develop**.

-----------------
Development Setup
-----------------

Choose one of the following setup options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Option 1: Local Development ("bare-metal")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option runs the application directly on your local machine.

**Setup Steps:**

1. **Set up Python environment:**

   **Important:** This project uses the Python version specified in `.python-version`. 
   Using the correct version is essential for compatibility.

   ::
   
      # Create and activate virtual environment
      python -m venv .venv
      source .venv/bin/activate


2. **Install Python dependencies:**
   ::
   
      # For development (includes test dependencies)
      pip install -r requirements/dev.txt
      
      # Or for production only
      pip install -r requirements.txt

3. **Set up local settings:**
   ::
   
      cp cdhweb/settings/local_settings.py.sample cdhweb/settings/local_settings.py
      
      # Edit local_settings.py and add your SECRET_KEY
      # Configure database connection to your local PostgreSQL

4. **Install Node.js dependencies:**
   ::
   
      npm install

5. **Set up database:**
   ::
   
      # Create database
      createdb cdhweb
      
      # Run migrations
      python manage.py migrate
      
      # Create admin user (choose one option):
      # Option A: Standard Django superuser
      python manage.py createsuperuser
      
      # Option B: Princeton NetID account with admin permissions  
      python manage.py createcasuser --admin netid

6. **Build frontend assets:**
   ::
   
      npm run build

7. **Collect static files:**
   ::
   
      python manage.py collectstatic --noinput

8. **Run the development server:**
   ::
   
      python manage.py runserver

9. **Visit the site:**
    - Main site: http://localhost:8000/
    - Django admin: http://localhost:8000/admin/
    - Wagtail admin: http://localhost:8000/cms/

**Additional Setup (Optional):**
- Download licensed fonts and install under `/sitemedia/fonts/`
- Install OpenCV dependencies for Wagtail image feature detection
- Set up pre-commit hooks: `pre-commit install`


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Option 2: Docker Development (Production-like Environment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option runs the application in Docker containers, providing a production-like environment.

**Setup Steps:**

1. **Download required files** from the shared Springload drive (https://drive.google.com/drive/folders/1B7qObEuO6sYJhVyE23RP8Tf0IbFCLlMf):
   - Database dump (e.g., `2024-05-02_cdhweb.sql`) --> put in `docker/database/`
   - Media archive (e.g., `2024-05-02_cdhweb_media.tar.gz`) --> put in `media/`
   - Font files --> put in `static_src/fonts/`

2. **Configure Docker settings:**
   ::
   
      cp cdhweb/settings/local_settings.py.docker-sample cdhweb/settings/local_settings.py

3. **Create Docker network:**
   ::
   
      docker network create nginx-proxy

4. **Start the application:**
   ::
   
      docker-compose up -d

5. **Build frontend assets (on host machine):**
   ::
   
      npm install
      npm run build

6. **Collect static files:**
   ::
   
      docker-compose exec application python manage.py collectstatic --noinput

7. **Run database migrations:**
   ::
   
      docker-compose exec application python manage.py migrate

8. **Create admin user (optional, choose one option):**
   ::
   
      # Option A: Standard Django superuser
      docker-compose exec application python manage.py createsuperuser
      
      # Option B: Princeton NetID account with admin permissions
      docker-compose exec application python manage.py createcasuser --admin netid

9. **Visit the site:**
    - Main site: http://localhost:56180/
    - Django admin: http://localhost:56180/admin/
    - Wagtail admin: http://localhost:56180/cms/



Frontend Development
~~~~~~~~~~~~~~~~~~~

The frontend uses webpack and npm.

1. **Set up Node.js version:**
::

   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   nvm use

2. **Install dependencies:**
::

   npm install

3. **Development mode:**
::

   npm start

4. **Build for production:**
::

   npm run build


Setup pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~

If you plan to contribute to this repository, please run the following command::

    pre-commit install

This will add a pre-commit hook to automatically style your python code with `black <https://github.com/psf/black>`_.

Because these styling conventions were instituted after multiple releases of
development on this project, ``git blame`` may not reflect the true author
of a given line. In order to see a more accurate ``git blame`` execute the
following command::

    git blame <FILE> --ignore-revs-file .git-blame-ignore-revs

  Or configure your git to always ignore styling revision commits:

    git config blame.ignoreRevsFile .git-blame-ignore-revs


Unit Testing
------------

Unit tests are written with `py.test <http://doc.pytest.org/>`_ but use
Django fixture loading and convenience testing methods when that makes
things easier.  To run them, first install test requirements (these are
included in dev)::

  pip install -r requirements/test.txt

Run tests using py.test::

  py.test


Visual Testing
--------------

Visual regression tests are written using the Python bindings for Selenium,
and DOM snapshots are uploaded to `Percy <https://percy.io/>`_. They run in CI
on pushes or pull requests to the `develop` branch.

Before visual tests are run, the CI build will execute::

  python manage.py create_test_site

Which uses existing pytest fixtures to populate the database with content
approximating a real website in order to execute the tests. It will then run::

  npm run test:visual

Which starts a Django development server and calls the `ci/visual_tests.py`
script to upload DOM snapshots to Percy for regression analysis.

You can use both of these commands locally if you need to accomplish either of
these tasks. You will need to have the dependencies in `requirements/test.txt`
installed, and set `PERCY_TOKEN` in your shell environment.


Documentation
~~~~~~~~~~~~~

Documentation is generated using `sphinx <http://www.sphinx-doc.org/>`__
To generate documentation, first install development requirements::

    pip install -r requirements/dev.txt

Then build the documentation using the customized make file in the `docs`
directory::

    cd sphinx-docs
    make html

When building documentation for a production release, use `make docs` to
update the published documentation on GitHub Pages.

On every commit, GitHub Actions will generate and then publish a database diagram to `dbdocs @ princetoncdh/cdh-web <https://dbdocs.io/princetoncdh/cdh-web>`_. But to generate locally, install and log into dbdocs. Then run::

    python manage.py dbml > cdhweb.dbml
    npx dbdocs build cdhweb.dbml --project cdhweb


License
-------
This project is licensed under the `Apache 2.0 License <https://github.com/Princeton-CDH/cdh-web/blob/main/LICENSE>`_.

©2023 Trustees of Princeton University.  Permission granted via
Princeton Docket #20-2634 for distribution online under a standard Open Source
license. Ownership rights transferred to Rebecca Koeser provided software
is distributed online via open source.