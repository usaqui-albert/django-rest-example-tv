from django.conf.urls import url


from .views import (
    AdminAuth, AdminUsersListView, AdminUserDetailView, AdminPetView,
    AdminUserDeactive, AdminVetVerificationView
)

urlpatterns = [
    url(r'^$', AdminUsersListView.as_view()),
    url(r'^(?P<pk>\d+)/$', AdminUserDetailView.as_view()),
    url(r'^(?P<pk>\d+)/pets/$', AdminPetView.as_view()),
    url(r'^(?P<pk>\d+)/sessions/$', AdminUserDeactive.as_view()),
    url(r'^(?P<pk>\d+)/verify/$', AdminVetVerificationView.as_view()),
    url(r'^login/$', AdminAuth.as_view()),
]
