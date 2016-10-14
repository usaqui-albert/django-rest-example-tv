from django.conf.urls import url

from .views import (
    PostPetOwnerListCreateView
)

urlpatterns = [
    url(r'^$', PostPetOwnerListCreateView.as_view()),
]
