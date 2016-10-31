from django.conf.urls import url

from comments.views import (
    CommentsPetOwnerListCreateView, CommentsVetListCreateView)

from .views import (
    PostListCreateView, PaidPostView, PostRetriveUpdateDeleteView,
    ImagePostDeleteView
)

urlpatterns = [
    url(r'^$', PostListCreateView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', PostRetriveUpdateDeleteView.as_view()),
    url(r'^(?P<pk>[0-9]+)/paid/$', PaidPostView.as_view()),
    url(r'^(?P<pk>[0-9]+)/vet-comment/$', CommentsVetListCreateView.as_view()),
    url(
        r'^(?P<pk>[0-9]+)/pet-comment/$',
        CommentsPetOwnerListCreateView.as_view()
    ),
    url(r'^images/(?P<pk>[0-9]+)/$', ImagePostDeleteView.as_view()),
]
