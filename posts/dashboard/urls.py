from django.conf.urls import url

from .views import AdminPostView, AdminActiveDeactivePostView


urlpatterns = [
    url(r'^$', AdminPostView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', AdminActiveDeactivePostView.as_view()),
]
