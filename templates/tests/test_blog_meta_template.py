"""
Simple tests for the templates/snippets/blog_meta.html template.
Tests COinS metadata for Zotero integration.
run 'docker-compose exec application python -m pytest templates/tests/test_blog_meta_template.py -v'
"""

from django.template import Context, Template
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from datetime import datetime


class MockPage:
    """Simple mock blog page object."""
    def __init__(self):
        self.title = "Test CDH Blog Post"
        self.search_description = "Test description"
        self.first_published_at = datetime(2025, 6, 26)
        self.owner = User(username="testuser", first_name="Test", last_name="User")
        
    class authors:
        @staticmethod
        def exists():
            return False
            
        @staticmethod
        def all():
            return []


class MockPageWithAuthors:
    """Mock blog page with authors."""
    def __init__(self):
        self.title = "Multi Author Post"
        self.search_description = "Post with multiple authors"
        self.first_published_at = datetime(2025, 6, 26)
        self.owner = User(username="testuser")
        
    class authors:
        @staticmethod
        def exists():
            return True
            
        @staticmethod
        def all():
            class MockAuthor:
                def __init__(self, name):
                    self.person = type('Person', (), {'__str__': lambda self: name})()
            return [MockAuthor("Author One"), MockAuthor("Author Two")]


class MockPageNoAbstract:
    """Mock blog page with no abstract content."""
    def __init__(self):
        self.title = "Post Without Abstract"
        self.search_description = ""  # Empty string
        self.first_published_at = datetime(2025, 6, 26)
        self.owner = User(username="testuser")
        
    class authors:
        @staticmethod
        def exists():
            return False
            
        @staticmethod
        def all():
            return []


class TestBlogMetaTemplate(TestCase):
    """Very simple tests for blog_meta.html template."""

    def setUp(self):
        self.factory = RequestFactory()
        self.template_content = """
        {% load wagtailcore_tags %}
        {% include 'snippets/blog_meta.html' %}
        """


    def render_template(self, page):
        """Helper to render the template."""
        request = self.factory.get("/test/")
        request.build_absolute_uri = lambda: "https://example.com/test/"
        
        template = Template(self.template_content)
        context = Context({'page': page, 'request': request})
        return template.render(context)


    def test_coins_span_present(self):
        """Test that COinS span element is present."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('<span class="Z3988"', rendered)
        self.assertIn('title="', rendered)


    def test_coins_blog_type_present(self):
        """Test that COinS identifies content as blogPost."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.type=blogPost', rendered)


    def test_coins_title_present(self):
        """Test that COinS contains the page title."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.title=Test%20CDH%20Blog%20Post', rendered)


    def test_coins_date_present(self):
        """Test that COinS contains the publication date."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.date=2025-06-26', rendered)


    def test_coins_source_present(self):
        """Test that COinS contains the source information."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.source=Center%20For%20Digital%20Humanities%40Princeton', rendered)


    def test_coins_url_present(self):
        """Test that COinS contains the page URL."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.identifier=https%3A//example.com/test/', rendered)


    def test_coins_author_multiple(self):
        """Test COinS with multiple authors."""
        page = MockPageWithAuthors()
        rendered = self.render_template(page)
        self.assertIn('rft.creator=Author%20One', rendered)
        self.assertIn('rft.creator=Author%20Two', rendered)


    def test_coins_author_fallback(self):
        """Test COinS falls back to page owner when no authors."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.creator=Test%20User', rendered)


    def test_coins_description_present(self):
        """Test that COinS contains description when available."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('rft.description=Test%20description', rendered)


    def test_coins_description_absent_when_empty(self):
        """Test that COinS doesn't include description when empty."""
        page = MockPageNoAbstract()
        rendered = self.render_template(page)
        self.assertNotIn('rft.description=', rendered)


    def test_coins_all_basic_elements_present(self):
        """Test that all basic COinS elements are present."""
        page = MockPage()
        rendered = self.render_template(page)
        
        required_elements = [
            'url_ver=Z39.88-2004',
            'ctx_ver=Z39.88-2004',
            'rft_val_fmt=info:ofi/fmt:kev:mtx:dc',
            'rft.type=blogPost',
            'rft.title=',
            'rft.creator=',
            'rft.date=',
            'rft.source=',
            'rft.identifier='
        ]
        
        for element in required_elements:
            self.assertIn(element, rendered)
        
