from django.conf.urls import url

from .views import (
    UserAuth, UserCreateView, UserListView, VeterinarianListCreateView,
    BreederListCreateView, GroupsListView
)

urlpatterns = [
    url(r'^$', UserListView.as_view()),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^groups/$', GroupsListView.as_view()),
    url(r'^create/$', UserCreateView.as_view()),
    url(r'^breeder/$', BreederListCreateView.as_view()),
    url(r'^veterinarian/$', VeterinarianListCreateView.as_view()),
]
