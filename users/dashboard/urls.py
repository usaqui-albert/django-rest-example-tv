from django.conf.urls import url


from .views import (
    AdminAuth, AdminUsersListView
)

urlpatterns = [
    url(r'^$', AdminUsersListView.as_view()),
    url(r'^login/$', AdminAuth.as_view()),
]
