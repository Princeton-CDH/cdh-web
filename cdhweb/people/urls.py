from django.conf.urls import url

from cdhweb.people import views


urlpatterns = [
    # for now, no generic people list page exists
    # url('^$', views.ProfileListView.as_view(), name='list'),
    url(r'^staff/$', views.StaffListView.as_view(), name='staff'),
    url(r'^postdocs/$', views.PostdocListView.as_view(), name='postdocs'),
    url(r'^students/$', views.StudentListView.as_view(), name='students'),
    url(r'^faculty/$', views.FacultyListView.as_view(), name='faculty'),
    url(r'^speakers/$', views.SpeakerListView.as_view(), name='speakers'),
    url(r'^executive-committee/$', views.ExecListView.as_view(), name='exec-committee'),

    url(r'^(?P<slug>[\w-]+)/$', views.ProfileDetailView.as_view(), name='profile'),
]