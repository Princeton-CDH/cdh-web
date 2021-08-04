from cdhweb.pages.forms import SiteSearchForm
from cdhweb.pages.models import PageIntro


def page_intro(request):
    """Template context processor: if there is a PageIntro snippet
    for this page, add it to the context for display."""
    # wagtail stores link url without leading and trailing slashes,
    # but requests to django view urls include them; strip them off to match

    # NOTE: page intro modification time is NOT taken into account
    # when generating Last-Modified headers and returning 304 Not Modified
    page_intro = PageIntro.objects.filter(
        page__link_url=request.path.strip("/")
    ).first()
    if page_intro:
        return {"page_intro": page_intro}
    return {}


def site_search(request):
    """Template context processor: adds site search form to context."""
    return {"site_search": SiteSearchForm()}
