from django.conf.urls import url

from .views import AdminPostView, AdminPostDetailView


urlpatterns = [
    url(r'^$', AdminPostView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', AdminPostDetailView.as_view()),
]
