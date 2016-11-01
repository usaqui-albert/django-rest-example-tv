from django.conf.urls import url

from .views import CommentVoteView


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/vote/$', CommentVoteView.as_view()),
]
