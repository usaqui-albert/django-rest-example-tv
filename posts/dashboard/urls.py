from django.conf.urls import url

from .views import (
    AdminPostView, AdminActiveDeactivePostView, AdminPostDetailView
)


urlpatterns = [
    url(r'^$', AdminPostView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', AdminPostDetailView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', AdminActiveDeactivePostView.as_view()),
]
