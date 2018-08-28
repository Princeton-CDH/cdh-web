from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
import pytest

from cdhweb.resources.models import Attachment, ResourceType, DateRange


class TestAttachment(TestCase):

    def test_str(self):
        attach = Attachment(title='My Document')
        assert str(attach) == attach.title

        attach.attachment_type = 'PDF'
        assert str(attach) == '%s (%s)' % (attach.title, attach.attachment_type)

        attach.author = 'Person'
        assert str(attach) == '%s, %s (%s)' % (attach.title, attach.author,
            attach.attachment_type)

        attach.attachment_type = None
        assert str(attach) == '%s, %s' % (attach.title, attach.author)


class TestResourceType(TestCase):

    def test_str(self):
        restype = ResourceType(name='twitter')
        assert str(restype) == restype.name


class TestDateRange(TestCase):

    def test_is_current(self):
        # start date in past, no end date
        span = DateRange(start_date=date.today() - timedelta(days=50))
        assert span.is_current

        # end date in future
        span.end_date = date.today() + timedelta(days=30)
        assert span.is_current

        # end date in past
        span.end_date = date.today() - timedelta(days=3)
        assert not span.is_current

        # end date = today, current
        span.end_date = date.today()
        assert span.is_current

        # start date in future
        span.start_date = date.today() + timedelta(days=3)
        assert not span.is_current

    def test_years(self):
        # start date, no end date
        span = DateRange(start_date=date(2016, 6, 1))
        assert span.years == '2016–'
        # end date same year as start
        span.end_date = date(2016, 12, 1)
        assert span.years == '2016'

        # end date known, different year
        span.end_date = date(2017, 12, 1)
        assert span.years == '2016–2017'

    def test_clean_fields(self):
        with pytest.raises(ValidationError):
            DateRange(start_date=date(1901, 1, 1), end_date=date(1900, 1, 1)).clean_fields()

        # should not raise exception
        # - end after start
        DateRange(start_date=date(1901, 1, 1), end_date=date(1905, 1, 1)) \
            .clean_fields()
        # - only start date set
        DateRange(start_date=date(1901, 1, 1)).clean_fields()
        # exclude set
        DateRange(start_date=date(1901, 1, 1), end_date=date(1900, 1, 1)) \
                .clean_fields(exclude=['start_date'])
        DateRange(start_date=date(1901, 1, 1), end_date=date(1900, 1, 1)) \
                .clean_fields(exclude=['end_date'])
