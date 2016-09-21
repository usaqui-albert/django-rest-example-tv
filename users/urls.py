from django.conf.urls import url

from .views import (
    UserAuth, UserView, VeterinarianListCreateView,
    BreederListCreateView, GroupsListView, UserGetUpdateView,
    AuthorizeBreederView, AuthorizeVetView, AreaInterestListView
)

urlpatterns = [
    url(r'^$', UserView.as_view()),
    url(r'^(?P<pk>\d+)/$', UserGetUpdateView.as_view()),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^groups/$', GroupsListView.as_view()),
    url(r'^breeder/$', BreederListCreateView.as_view()),
    url(r'^breeder/(?P<pk>\d+)/verify/$', AuthorizeBreederView.as_view()),
    url(r'^veterinarian/$', VeterinarianListCreateView.as_view()),
    url(r'^veterinarian/(?P<pk>\d+)/verify/$', AuthorizeVetView.as_view()),
    url(r'^veterinarian/area-interest/$', AreaInterestListView.as_view()),
]
