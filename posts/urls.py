from django.conf.urls import url

from .views import (
    PostVetListCreateView
)

urlpatterns = [
    url(r'^$', PostVetListCreateView.as_view()),
]
