from django.conf.urls import url

from pets.views import PetListByUser

from .views import (
    UserAuth, UserView, VeterinarianListCreateView,
    BreederListCreateView, GroupsListView,
    AuthorizeBreederView, AuthorizeVetView, AreaInterestListView,
    UserRetrieveUpdateView, StripeCustomerView
)

urlpatterns = [
    url(r'^$', UserView.as_view()),
    url(r'^(?P<pk>\d+)/$', UserRetrieveUpdateView.as_view()),
    url(r'^(?P<pk>\d+)/pets/$', PetListByUser.as_view()),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^groups/$', GroupsListView.as_view()),
    url(r'^breeders/$', BreederListCreateView.as_view()),
    url(r'^breeders/(?P<pk>\d+)/verify/$', AuthorizeBreederView.as_view()),
    url(r'^veterinarians/$', VeterinarianListCreateView.as_view()),
    url(r'^veterinarians/(?P<pk>\d+)/verify/$', AuthorizeVetView.as_view()),
    url(r'^veterinarians/area-interests/$', AreaInterestListView.as_view()),
    url(r'^(?P<pk>\d+)/payments/$', StripeCustomerView.as_view()),
]
