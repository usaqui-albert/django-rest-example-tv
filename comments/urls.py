from django.conf.urls import url

from .views import CommentVoteView, FeedbackCreateView


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/vote/$', CommentVoteView.as_view()),
    url(r'^(?P<pk>[0-9]+)/feedbacks/$', FeedbackCreateView.as_view()),
]
