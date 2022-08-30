from datetime import date, timedelta
from unittest.mock import PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError

from cdhweb.pages.models import (
    DateRange,
    DisplayUrlMixin,
    ExternalAttachment,
    LocalAttachment,
    RelatedLinkType,
)


class TestRelatedLinkType:
    def test_str(self):
        restype = RelatedLinkType(name="twitter")
        assert str(restype) == restype.name


class DateRangeTestModel(DateRange):
    class Meta:
        managed = False


class TestLocalAttachment:
    @patch.object(
        LocalAttachment,
        "file_extension",
        new_callable=PropertyMock,
        return_value="docx",
    )
    def test_str(self, file_ext, db):
        """Local attachment should identify title, author, and file extension"""
        attachment = LocalAttachment(title="My Attachment")
        attachment.title = "My Attachment"
        # no author
        assert str(attachment) == "My Attachment (docx)"
        # with author
        attachment.author = "John Smith"
        assert str(attachment) == "My Attachment, John Smith (docx)"


class TestExternalAttachment:
    def test_str(self, db):
        """External attachment should identify title, author, and display url"""
        attachment = ExternalAttachment(
            title="My External Attachment", url="https://google.com?q=foobar"
        )
        # no author
        assert str(attachment) == "My External Attachment (google.com)"
        # with author
        attachment.author = "John Smith"
        assert str(attachment) == "My External Attachment, John Smith (google.com)"


class TestDisplayUrlMixin:
    def test_display_url(self, db):
        """Display URL should remove scheme, params, query, fragment, slashes"""

        class MyDisplayUrlModel(DisplayUrlMixin):
            pass

        model = MyDisplayUrlModel(url="https://google.com/")
        assert model.display_url == "google.com"
        model.url = "http://google.com/foo/bar/baz/"
        assert model.display_url == "google.com/foo/bar/baz"
        model.url = "http://google.com?query=foo"
        assert model.display_url == "google.com"
        model.url = "http://google.com/myplace#subplace"
        assert model.display_url == "google.com/myplace"


class TestDateRange:
    def test_is_current(self):
        # start date in past, no end date
        span = DateRangeTestModel(start_date=date.today() - timedelta(days=50))
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
        span = DateRangeTestModel(start_date=date(2016, 6, 1))
        assert span.years == "2016–"
        # end date same year as start
        span.end_date = date(2016, 12, 1)
        assert span.years == "2016"

        # end date known, different year
        span.end_date = date(2017, 12, 1)
        assert span.years == "2016–2017"

    def test_clean_fields(self):
        with pytest.raises(ValidationError):
            DateRangeTestModel(
                start_date=date(1901, 1, 1), end_date=date(1900, 1, 1)
            ).clean_fields()

        # should not raise exception
        # - end after start
        DateRangeTestModel(
            start_date=date(1901, 1, 1), end_date=date(1905, 1, 1)
        ).clean_fields()
        # - only start date set
        DateRangeTestModel(start_date=date(1901, 1, 1)).clean_fields()
        # exclude set
        DateRangeTestModel(
            start_date=date(1901, 1, 1), end_date=date(1900, 1, 1)
        ).clean_fields(exclude=["start_date"])
        DateRangeTestModel(
            start_date=date(1901, 1, 1), end_date=date(1900, 1, 1)
        ).clean_fields(exclude=["end_date"])
