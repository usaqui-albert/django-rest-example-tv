from django.conf.urls import url

from .views import UserAuth, UserCreateView, UserListView

urlpatterns = [
    url(r'^login/$', UserAuth.as_view()),
    url(r'^user/create$', UserCreateView.as_view()),
    url(r'^$', UserListView.as_view()),
]
