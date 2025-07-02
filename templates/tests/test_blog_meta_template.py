"""
Simple tests for the templates/snippets/blog_meta.html template.
Tests basic Zotero citation metadata tags.
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


    def test_citation_title_present(self):
        """Test that citation_title meta tag is present."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('<meta name="citation_title"', rendered)
        self.assertIn('Test CDH Blog Post', rendered)


    def test_citation_date_present(self):
        """Test that citation_date meta tag is present."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('<meta name="citation_date"', rendered)
        

    def test_citation_language_present(self):
        """Test that citation_language meta tag is present."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('<meta name="citation_language"', rendered)
        self.assertIn('content="en"', rendered)


    def test_citation_author_multiple(self):
        """Test citation_author with multiple authors."""
        page = MockPageWithAuthors()
        rendered = self.render_template(page)
        self.assertIn('<meta name="citation_author"', rendered)
        self.assertIn('Author One', rendered)
        self.assertIn('Author Two', rendered)


    def test_citation_webpage_url_present(self):
        """Test that citation_webpage_url meta tag is present."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('<meta name="citation_webpage_url"', rendered)
        self.assertIn('https://example.com/test/', rendered)


    def test_citation_abstract_present(self):
        """Test that citation_abstract meta tag is present when there's content."""
        page = MockPage()
        rendered = self.render_template(page)
        self.assertIn('<meta name="citation_abstract"', rendered)
        self.assertIn('Test description', rendered)


    def test_all_basic_meta_tags_present(self):
        """Test that all basic Zotero meta tags are present when content is available."""
        page = MockPage()
        rendered = self.render_template(page)
        
        required_tags = [
            'citation_title',
            'citation_date',
            'citation_webpage_title', 
            'citation_webpage_url',
            'citation_language',
            'citation_author'
        ]
        
        for tag in required_tags:
            self.assertIn(f'<meta name="{tag}"', rendered)
            
        # Abstract should be present when there's content
        self.assertIn('<meta name="citation_abstract"', rendered)
        
