from django.conf.urls import url

from cdhweb.projects import views


urlpatterns = [
    url('^$', views.ProjectListView.as_view(), name='list'),
    url('^staff/$', views.StaffProjectListView.as_view(), name='staff'),
    url(r'^(?P<slug>[\w-]+)/$', views.ProjectDetailView.as_view(), name='detail'),
]
