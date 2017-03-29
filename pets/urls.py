from django.conf.urls import url

from .views import (
    PetCreateView, PetRetrieveUpdateDeleteView, PetTypeListView
)

urlpatterns = [
    url(r'^$', PetCreateView.as_view()),
    url(r'^(?P<pk>\d+)/$', PetRetrieveUpdateDeleteView.as_view()),
    url(r'^pet-types/$', PetTypeListView.as_view()),
]
