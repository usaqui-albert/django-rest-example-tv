from django.conf.urls import url

from .views import (
    PetsListCreateView, PetRetrieveUpdateDeleteView,
    PetTypeListView
)

urlpatterns = [
    url(r'^$', PetsListCreateView.as_view()),
    url(r'^(?P<pk>\d+)/$', PetRetrieveUpdateDeleteView.as_view()),
    url(r'^pet-types/$', PetTypeListView.as_view()),
]
