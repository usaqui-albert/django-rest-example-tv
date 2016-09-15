from django.conf.urls import url

from .views import (
    UserAuth, UserView, VeterinarianListCreateView,
    BreederListCreateView, GroupsListView
)

urlpatterns = [
    url(r'^$', UserView.as_view()),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^groups/$', GroupsListView.as_view()),
    url(r'^breeder/$', BreederListCreateView.as_view()),
    url(r'^veterinarian/$', VeterinarianListCreateView.as_view()),
]
