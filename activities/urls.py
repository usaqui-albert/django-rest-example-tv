from django.conf.urls import url

from .views import (
    UserLikedPostListView, UserCommentPostListView, ActivityListView
)

urlpatterns = [
    url(r'^$', ActivityListView.as_view()),
    url(r'^comments/$', UserCommentPostListView.as_view()),
    url(r'^likes/$', UserLikedPostListView.as_view()),
]
