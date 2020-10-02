CDH Website
===========
open and improve ur self.
.. sphinx-start-marker-do-not-remove

.. image:: https://travis-ci.org/Princeton-CDH/cdh-web.svg?branch=master
   :target: https://travis-ci.org/Princeton-CDH/cdh-web
   :alt: Build status

.. image:: https://landscape.io/github/Princeton-CDH/cdh-web/master/landscape.svg?style=flat
  :target: https://landscape.io/github/Princeton-CDH/cdh-web/master
  :alt: Code Health

.. image:: https://codecov.io/gh/Princeton-CDH/cdh-web/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Princeton-CDH/cdh-web
   :alt: Code coverage

.. image:: https://requires.io/github/Princeton-CDH/cdh-web/requirements.svg?branch=master
   :target: https://requires.io/github/Princeton-CDH/cdh-web/requirements/?branch=master
   :alt: Requirements Status

Python 3.5 / Django 1.11 / Node 8.16.0 / MariaDB (MySQL) 5.5 w/ timezone info

`cdhweb` is a Django+Mezzanine application that powers the CDH website
with custom models for people, events, and projects.

View `software and architecture documentation <https://princeton-cdh.github.io/cdh-web/>`_
for the current release.

This repository uses `git-flow <https://github.com/nvie/gitflow>`_ conventions; master
contains the most recent release, and work in progress will be on the develop branch.
Pull requests should be made against develop.


Development instructions
------------------------

Initial setup and installation:

- Recommended: create and activate a python 3.5 virtualenv::

    virtualenv cdhweb -p python3.5
    source cdhweb/bin/activate

- Use pip to install required python dependencies.  To install production
  dependencies only::

    pip install -r requirements.txt

  To install all development requirements::

    pip install -r requirements/dev.txt

- Install django-compressor dependencies::

    npm install

- Copy sample local settings and configure for your environment::

    cp cdhweb/local_settings.py.sample cdhweb/local_settings.py

Remember to add a ``SECRET_KEY`` setting!

- Download licensed fonts and install locally under /sitemedia/fonts/

- If running this application on MariaDB/MySQL, you must make sure that
  time zone definitions are installed. On most flavors of Linux/MacOS,
  you may use the following command, which will prompt
  for the database server's root password::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql -p

  If this command does not work, make sure you have the command line utilities
  for MariaDB/MySQL installed and consult the documentation for your OS for
  timezone info. Windows users will need to install a copy of the zoneinfo
  files.

  See `MariaDB <https://mariadb.com/kb/en/library/mysql_tzinfo_to_sql/>`_'s
  info on the utility for more information.

Unit Testing
------------

Unit tests are written with `py.test <http://doc.pytest.org/>`_ but use
Django fixture loading and convenience testing methods when that makes
things easier.  To run them, first install test requirements (these are
included in dev)::

  pip install -r requirements/test.txt

Run tests using py.test::

  py.test

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

License
-------
This project is licensed under the `Apache 2.0 License <https://github.com/Princeton-CDH/ppa-django/blob/master/LICENSE>`_.

©2019 Trustees of Princeton University.  Permission granted via
Princeton Docket #20-2634 for distribution online under a standard Open Source
license. Ownership rights transferred to Rebecca Koeser provided software
is distributed online via open source.
