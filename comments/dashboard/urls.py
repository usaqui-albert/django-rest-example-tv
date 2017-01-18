from django.conf.urls import url

from .views import AdminFeedbackListView

urlpatterns = [
    url(r'^$', AdminFeedbackListView.as_view()),
]
