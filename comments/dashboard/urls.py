from django.conf.urls import url

from .views import AdminFeedbackListView, AdminFeedbackView

urlpatterns = [
    url(r'^$', AdminFeedbackListView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', AdminFeedbackView.as_view()),
]
