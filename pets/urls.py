from django.conf.urls import url

from .views import (
    PetsListCreateView
)

urlpatterns = [
    url(r'^$', PetsListCreateView.as_view()),
]
