from django.conf.urls import url

from .views import (
    PetsListCreateView, PetRetriveUpdateDeleteView,
    PetTypeListView
)

urlpatterns = [
    url(r'^$', PetsListCreateView.as_view()),
    url(r'^(?P<pk>\d+)/$', PetRetriveUpdateDeleteView.as_view()),
    url(r'^pet-types/$', PetTypeListView.as_view()),
]
