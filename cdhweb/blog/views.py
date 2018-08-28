from datetime import datetime

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.views.generic.detail import DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, \
    MonthArchiveView

from cdhweb.blog.models import BlogPost
from cdhweb.resources.utils import absolutize_url
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin


class BlogPostMixinView(object):
    '''View mixin that sets model to Blogpost and returns a
    published BlogPost queryset.'''
    model = BlogPost

    def get_queryset(self):
        # use displayable manager to find published events only
        # (or draft profiles for logged in users with permission to view)
        return BlogPost.objects.published() # TODO: published(for_user=self.request.user)


class BlogPostArchiveMixin(BlogPostMixinView, LastModifiedListMixin):
    '''Mixin with common settings for blogpost archive views'''
    date_field = 'publish_date'
    context_object_name = 'blogposts'
    make_object_list = True
    paginate_by = 12
    template_name = 'blog/blogpost_archive.html'


class BlogIndexView(BlogPostArchiveMixin, ArchiveIndexView):
    '''Main blog post list view'''
    date_list_period = 'month'


class BlogYearArchiveView(BlogPostArchiveMixin, YearArchiveView):
    '''Blog post archive by year'''

    def get_context_data(self, *args, **kwargs):
        context = super(BlogYearArchiveView, self).get_context_data(*args, **kwargs)
        context.update({
            'date_list': BlogPost.objects.dates('publish_date', 'month', order='DESC'),
            'title': self.kwargs['year']
        })
        return context


class BlogMonthArchiveView(BlogPostArchiveMixin, MonthArchiveView):
    '''Blog post archive by month'''
    month_format = '%m'

    def get_context_data(self, *args, **kwargs):
        context = super(BlogMonthArchiveView, self).get_context_data(*args, **kwargs)
        # current requested month/year for display
        date = datetime.strptime('%(year)s %(month)s' % self.kwargs, '%Y %m')
        context.update({
            'date_list': BlogPost.objects.dates('publish_date', 'month', order='DESC'),
            'title': date.strftime('%B %Y')
        })
        return context


class BlogDetailView(BlogPostMixinView, DetailView, LastModifiedMixin):
    '''Blog post detail view'''

    def get_context_data(self, *args, **kwargs):
        context = super(BlogDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context.update({
            'page': self.object,
            'opengraph_type': 'article',
            'next': self.object.get_next_by_publish_date(),
            'previous': self.object.get_previous_by_publish_date(),
        })
        return context


class RssBlogPostFeed(Feed):
    '''Blog post RSS feed'''
    title = "Center for Digital Humanities @ Princeton University Updates"
    link = "/updates/"
    description = "Updates and news on work from the Center for Digital Humanities @ Princeton University"

    def items(self):
        '''ten most recent blog posts, ordered by publish date'''
        return BlogPost.objects.order_by('-publish_date')[:10]

    def item_title(self, item):
        '''blog post title'''
        return item.title

    def item_description(self, item):
        '''blog post description, for feed content'''
        return item.content

    def item_link(self, item):
        '''absolute link to blog post'''
        return absolutize_url(item.get_absolute_url())

    def item_author_name(self, item):
        '''author of the blog post; comma-separated list for multiple'''
        return ', '.join([str(auth) for auth in item.users.all()])

    def item_author_link(self, item):
        '''link to author profile page, if there is only one author and
        the author has a published profile'''
        if item.users.count() == 1:
            author = item.users.first()
            if author.published():
                return absolutize_url(author.get_absolute_url())

    def item_pubdate(self, item):
        '''publication date'''
        return item.publish_date

    def item_updatedate(self, item):
        '''last modified date'''
        return item.updated

    def item_categories(self, item):
        '''keyword category terms'''
        return [str(kw) for kw in item.keywords.all()]


class AtomBlogPostFeed(RssBlogPostFeed):
    '''Blog post Atom feed'''

    feed_type = Atom1Feed
    subtitle = RssBlogPostFeed.description
