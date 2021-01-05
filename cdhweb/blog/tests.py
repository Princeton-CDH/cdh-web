from unittest import skip
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.html import escape
from mezzanine.core.models import CONTENT_STATUS_DRAFT

from cdhweb.blog.models import BlogPost
from cdhweb.blog.views import RssBlogPostFeed
from cdhweb.blog.sitemaps import BlogPostSitemap


class TestBlog(TestCase):

    def test_get_absolute_url(self):
        jan15 = datetime(2016, 1, 15)
        post = BlogPost(publish_date=jan15, slug='news-and-updates')
        # single-digit months should be converted to two-digit for url
        resolved_url = resolve(post.get_absolute_url())
        assert resolved_url.namespace == 'blog'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['year'] == str(post.publish_date.year)
        assert resolved_url.kwargs['month'] == '%02d' % post.publish_date.month
        assert resolved_url.kwargs['slug'] == post.slug

    def test_short_title(self):
        '''test that truncated titles are correctly generated'''
        # truncate with ellipsis for titles > 75char
        post = BlogPost(
            title="Congratulations to Valedictorian Jin Yun Chow '17 and Salutatorian Grant Storey '17")
        assert len(post.short_title) == 65
        assert post.short_title.endswith('…')
        # do nothing for titles < 75char
        post = BlogPost(title="Congratulations!")
        assert post.short_title == post.title

    def test_short_description(self):
        '''test that truncated descriptions are correctly generated'''
        # truncate with ellipsis for descriptions > 250char
        post = BlogPost(description="The CDH is hiring! \u00a0We are looking for a curious, committed, and collegial colleague to join our Development and Design Team as our second Digital Humanities\u00a0Developer. You will work with database designers, UX designers, project managers, fellow programmers\u00a0and the faculty, students and staff of Princeton University to create innovating\u00a0projects and contribute back to the Open Source software community. \u00a0")
        assert len(post.short_description) == 250
        assert post.short_description.endswith('…')
        # do nothing for descriptions < 250char
        post = BlogPost(description="The CDH is hiring!")
        assert post.short_description == post.description


class TestViews(TestCase):
    fixtures = ['test_blogposts.json']

    @skip("fixme")
    def test_rss_feed(self):
        post = BlogPost.objects.get(pk=1)

        response = self.client.get(reverse('blog:rss'))
        assert response['content-type'] == 'application/rss+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)
        # check for post content
        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, escape(post.content[:100]))

        # post with author
        authorpost = BlogPost.objects.filter(users__isnull=False).first()
        self.assertContains(response, str(authorpost.users.first()))

        # draft post should *NOT* be included
        post.status = CONTENT_STATUS_DRAFT
        post.save()
        response = self.client.get(reverse('blog:rss'))
        self.assertNotContains(response, post.get_absolute_url())

        # TODO: author with published profile page, multiple authors

    @skip("fixme")
    def test_atom_feed(self):
        response = self.client.get(reverse('blog:atom'))
        assert response['content-type'] == 'application/atom+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)

    def test_index(self):
        response = self.client.get(reverse('blog:list'))

        # title displays
        self.assertContains(response, 'Latest Updates')

        for post in BlogPost.objects.published():
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())
            self.assertContains(response, post.description)
            for auth in post.users.all():
                self.assertContains(response, str(auth))

            # links to blog archive by montth
            self.assertContains(response,
                                reverse('blog:by-month', kwargs={'year': post.publish_date.year,
                                                                 'month': post.publish_date.strftime('%m')}))

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

    def test_blogpost_detail(self):
        post = BlogPost.objects.order_by('publish_date').first()
        second_post = BlogPost.objects.order_by('publish_date')[1]
        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, post.description)
        for auth in post.users.all():
            self.assertContains(response, str(auth))

        self.assertContains(response, ', '.join(post.keywords.all()))

        # keywords & description in header
        self.assertContains(response,
                            '<meta name="keywords" content="%s"/>' % ', '.join(post.keywords.all()))
        self.assertContains(response,
                            '<meta name="description" content="%s"/>' % post.description)

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

        # next/previous links
        # first post has next and no previous
        self.assertContains(response, second_post.title)
        self.assertContains(response, second_post.get_absolute_url())
        self.assertContains(response, 'rel="next"')
        self.assertNotContains(response, 'rel="prev"')

        # second post has previous and no next
        response = self.client.get(second_post.get_absolute_url())
        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, 'rel="prev"')
        self.assertNotContains(response, 'rel="next"')

    def test_blogs_by_year(self):
        response = self.client.get(
            reverse('blog:by-year', kwargs={'year': 2017}))

        assert response.context['title'] == '2017'
        # date-specific title displays
        self.assertContains(response, '2017 Updates')
        # links to blog archive by montth
        self.assertContains(response,
                            reverse('blog:by-month', kwargs={'year': 2017, 'month': '09'}))

        # date filtering is really django logic, this is just
        # a sanity check for display
        for post in BlogPost.objects.published().filter(publish_date__year=2017):
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())

        for post in BlogPost.objects.published().exclude(publish_date__year=2017):
            self.assertNotContains(response, post.title)
            self.assertNotContains(response, post.get_absolute_url())

    def test_blogs_by_month(self):
        response = self.client.get(reverse('blog:by-month',
                                           kwargs={'year': 2017, 'month': '09'}))

        assert response.context['title'] == 'September 2017'
        # date-specific title displays
        self.assertContains(response, 'September 2017 Updates')

        # date filtering is really django logic, this is just
        # a sanity check for display
        for post in BlogPost.objects.filter(publish_date__year=2017,
                                            publish_date__month=9):
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())

        for post in BlogPost.objects.exclude(publish_date__year=2017,
                                             publish_date__month=9):
            self.assertNotContains(response, post.title)
            self.assertNotContains(response, post.get_absolute_url())


class TestBlogPostQuerySet(TestCase):

    def test_featured(self):
        post = BlogPost.objects.create()

        assert not BlogPost.objects.featured().exists()

        post.is_featured = True
        post.save()
        assert BlogPost.objects.featured().exists()

    def test_recent(self):
        # use django timezone util for timezone-aware datetime
        yesterday = timezone.now() - timedelta(days=1)
        oldest = timezone.now() - timedelta(days=10)
        today_post = BlogPost.objects.create(publish_date=timezone.now())
        yesterday_post = BlogPost.objects.create(publish_date=yesterday)
        oldest_post = BlogPost.objects.create(publish_date=oldest)

        recent = list(BlogPost.objects.recent())
        # most recent listed first
        assert today_post == recent[0]
        assert yesterday_post == recent[1]
        assert oldest_post == recent[2]


class TestBlogPostSitemap(TestCase):
    fixtures = ['test_blogposts.json']

    def test_items(self):
        sitemap = BlogPostSitemap()
        items = sitemap.items()

        # all published posts are present
        for post in BlogPost.objects.published():
            assert post in items

        # draft post is not present
        draft_post = BlogPost.objects.get(pk=3)
        assert draft_post not in items

        # featured posts have priority 0.6
        featured_post = BlogPost.objects.get(pk=1)
        assert sitemap.priority(featured_post) == 0.6

        # non-featured posts have default priority
        non_featured_post = BlogPost.objects.get(pk=23)
        assert sitemap.priority(non_featured_post) is None
