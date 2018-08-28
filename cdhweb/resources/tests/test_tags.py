from django.contrib.sites.models import Site
import pytest

from cdhweb.resources.templatetags import cdh_tags

def test_url_to_icon():
    assert cdh_tags.url_to_icon('/people/staff/') == 'ppl'
    assert cdh_tags.url_to_icon('/projects/') == 'folder'
    assert cdh_tags.url_to_icon('/events/') == 'cal'
    assert cdh_tags.url_to_icon('/contact/') == 'convo'
    assert cdh_tags.url_to_icon('/grants/seed-grant/') == 'seed'
    assert cdh_tags.url_to_icon('/graduate-fellowships/') == 'medal'
    assert cdh_tags.url_to_icon('/grants/') == 'grant'
    assert cdh_tags.url_to_icon('/unknown/') == ''
    assert cdh_tags.url_to_icon(None) == ''


@pytest.mark.django_db
def test_url_to_icon_path():
    domain = Site.objects.get_current().domain
    assert cdh_tags.url_to_icon_path('/people/staff/') == 'https://{}/static/img/cdh-icons/ppl.svg'.format(domain)
    # assert cdh_tags.url_to_icon('/projects/') == 'folder'
    # assert cdh_tags.url_to_icon('/events/') == 'cal'
    # assert cdh_tags.url_to_icon('/contact/') == 'convo'
    # assert cdh_tags.url_to_icon('/grants/seed-grant/') == 'seed'
    # assert cdh_tags.url_to_icon('/graduate-fellowships/') == 'medal'
    # assert cdh_tags.url_to_icon('/grants/') == 'grant'
    # assert cdh_tags.url_to_icon('/unknown/') == ''
