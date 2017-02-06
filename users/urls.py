from django.conf.urls import url

from pets.views import PetListByUser
from posts.views import PostByUserListView

from .views import (
    UserAuth, UserView, VeterinarianListCreateView,
    BreederListCreateView, GroupsListView, UserFeedBackView,
    AreaInterestListView, EmailToResetPasswordView, RestorePasswordView,
    UserRetrieveUpdateView, StripeCustomerView, UserFollowView, UserDeactive,
    ReferFriendView, UserFollowsListView, UserFollowedListView, DeviceView
)

urlpatterns = [
    url(r'^$', UserView.as_view()),
    url(r'^(?P<pk>\d+)/$', UserRetrieveUpdateView.as_view()),
    url(r'^(?P<pk>\d+)/follow/$', UserFollowView.as_view()),
    url(r'^(?P<pk>\d+)/follows/$', UserFollowsListView.as_view()),
    url(r'^(?P<pk>\d+)/followers/$', UserFollowedListView.as_view()),
    url(r'^(?P<pk>\d+)/payments/$', StripeCustomerView.as_view()),
    url(r'^(?P<pk>\d+)/pets/$', PetListByUser.as_view()),
    url(r'^(?P<pk>\d+)/posts/$', PostByUserListView.as_view()),
    url(r'^(?P<pk>\d+)/sessions/$', UserDeactive.as_view()),
    url(r'^breeders/$', BreederListCreateView.as_view()),
    url(r'^devices/$', DeviceView.as_view()),
    url(r'^feedback/$', UserFeedBackView.as_view()),
    url(r'^groups/$', GroupsListView.as_view()),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^refer/$', ReferFriendView.as_view()),
    url(r'^veterinarians/$', VeterinarianListCreateView.as_view()),
    url(r'^veterinarians/areas-of-interest/$', AreaInterestListView.as_view()),
    url(r'^reset-password/$', EmailToResetPasswordView.as_view()),
    url(r'^restore-password/$', RestorePasswordView.as_view()),

]
