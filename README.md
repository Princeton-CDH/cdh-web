# CDH Website Repo

[![Build Status](https://travis-ci.org/Princeton-CDH/cdh-web.svg?branch=develop)](https://travis-ci.org/Princeton-CDH/cdh-web)
[![codecov](https://codecov.io/gh/Princeton-CDH/cdh-web/branch/develop/graph/badge.svg)](https://codecov.io/gh/Princeton-CDH/cdh-web)
[![Code Health](https://landscape.io/github/Princeton-CDH/cdh-web/develop/landscape.svg?style=flat)](https://landscape.io/github/Princeton-CDH/cdh-web/develop)
[![Requirements Status](https://requires.io/github/Princeton-CDH/cdh-web/requirements.svg?branch=develop)](https://requires.io/github/Princeton-CDH/cdh-web/requirements/?branch=develop)


## Development instructions

Initial setup and installation:

- recommended: create and activate a python 3.5 virtualenv
    `virtualenv cdhweb -p python3.5`
    `source cdhweb/bin/activate`

- pip install required python dependencies
    `pip install -r requirements.txt`
    `pip install -r dev-requirements.txt`

- copy sample local settings and configure for your environment
    `cp cdhweb/local_settings.py.sample cdhweb/local_settings.py`

- download licensed fonts and install locally under /sitemedia

## Unit Testing

Unit tests are written with [py.test](http://doc.pytest.org/) but use Django fixture loading and convenience
testing methods when that makes things easier.  To run them, first install
development requirements:
```
pip install -r dev-requirements.txt
```

Run tests using py.test:
```
py.test
```
