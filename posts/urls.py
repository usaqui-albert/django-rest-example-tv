from django.conf.urls import url

from .views import (
    PostVetListCreateView, PaidPostView
)

urlpatterns = [
    url(r'^$', PostVetListCreateView.as_view()),
    url(r'^(?P<pk>[0-9]+)/paid/$', PaidPostView.as_view()),

]
