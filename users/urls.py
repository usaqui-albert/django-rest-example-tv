from django.conf.urls import url

from .views import (
    UserAuth, UserCreateView, UserListView, VeterinarianListCreateView,
    BreederListCreateView)

urlpatterns = [
    url(r'^$', UserListView.as_view()),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^user/create/$', UserCreateView.as_view()),
    url(r'^user/breeder/$', BreederListCreateView.as_view()),
    url(r'^user/veterinarian/$', VeterinarianListCreateView.as_view()),
]
