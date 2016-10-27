from django.conf.urls import url

from .views import (
    PostListCreateView, PaidPostView, PostRetriveUpdateDeleteView
)

urlpatterns = [
    url(r'^$', PostListCreateView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', PostRetriveUpdateDeleteView.as_view()),
    url(r'^(?P<pk>[0-9]+)/paid/$', PaidPostView.as_view()),
]
