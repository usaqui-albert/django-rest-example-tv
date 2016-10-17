from django.conf.urls import url

from .views import (
    PostListCreateView
)

urlpatterns = [
    url(r'^$', PostListCreateView.as_view()),
]
