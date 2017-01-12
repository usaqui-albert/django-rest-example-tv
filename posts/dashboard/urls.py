from django.conf.urls import url

from .views import (
    AdminPostView, AdminPostDetailView
)
from comments.dashboard.views import (
    PetOwnerCommentsView, VetCommentsView, AdminCommentDetailView
)


urlpatterns = [
    url(r'^$', AdminPostView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', AdminPostDetailView.as_view()),
    url(r'^(?P<pk>[0-9]+)/pet-comments/$', PetOwnerCommentsView.as_view()),
    url(r'^(?P<pk>[0-9]+)/vet-comments/$', VetCommentsView.as_view()),
    url(
        r'^(?P<pk_post>[0-9]+)/comments/(?P<pk_comment>[0-9]+)/$',
        AdminCommentDetailView.as_view()
    ),

]
