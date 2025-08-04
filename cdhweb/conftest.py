"""Fixtures/utilities that should be globally available for testing."""
# FIXME not sure how else to share fixtures that depend on other fixtures
# between modules - if you import just the top-level fixture (e.g. "events"),
# it fails to find the fixture dependencies, and so on all the way down. For
# now this does what we want, although it pollutes the namespace somewhat
from cdhweb.events.tests.conftest import *
from cdhweb.pages.tests.conftest import *
from cdhweb.people.tests.conftest import *
from cdhweb.projects.tests.conftest import *
