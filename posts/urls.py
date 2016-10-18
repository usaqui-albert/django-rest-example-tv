from django.conf.urls import url

from .views import (
    PostListCreateView, PaidPostView
)

urlpatterns = [
    url(r'^$', PostPetOwnerListCreateView.as_view()),
    url(r'^(?P<pk>[0-9]+)/paid/$', PaidPostView.as_view()),
]
