from django.conf.urls import url
from django.views.generic.base import RedirectView

app_name = 'people'
urlpatterns = [
    # redirect from /people/faculty -> /people/affiliates
    url(r'^faculty/$', RedirectView.as_view(url='/people/affiliates/', permanent=True)),
    # redirect from /people/postdocs -> /people/staff
    url(r'^postdocs/$', RedirectView.as_view(url='/people/staff/', permanent=True)),
]