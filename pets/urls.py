from django.conf.urls import url

from .views import (
    PetsListCreateView, PetRetriveUpdateDeleteView
)

urlpatterns = [
    url(r'^$', PetsListCreateView.as_view()),
    url(r'^(?P<pk>\d+)/$', PetRetriveUpdateDeleteView.as_view()),
]
