from django.conf.urls import url

from comments.views import (
    CommentsPetOwnerListCreateView, CommentsVetListCreateView)

from .views import (
    PostListCreateView, PaidPostView, PostRetrieveUpdateView,
    ImageDetailView, PostPaidListView, PostVoteView, PostReportView,
    ImageView
)

urlpatterns = [
    url(r'^$', PostListCreateView.as_view()),
    url(r'^paids/$', PostPaidListView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', PostRetrieveUpdateView.as_view()),
    url(r'^(?P<pk>[0-9]+)/paid/$', PaidPostView.as_view()),
    url(r'^(?P<pk>[0-9]+)/vote/$', PostVoteView.as_view()),
    url(
        r'^(?P<pk>[0-9]+)/vet-comments/$',
        CommentsVetListCreateView.as_view()),
    url(
        r'^(?P<pk>[0-9]+)/pet-comments/$',
        CommentsPetOwnerListCreateView.as_view()
    ),
    url(r'^(?P<pk>[0-9]+)/images/$', ImageView.as_view()),
    url(
        r'^(?P<pk_post>[0-9]+)/images/(?P<pk_image>[0-9]+)/$',
        ImageDetailView.as_view()
    ),
    url(r'^(?P<pk>\d+)/reports/$', PostReportView.as_view()),
]
