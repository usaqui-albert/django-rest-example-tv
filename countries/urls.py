from django.conf.urls import url

from .views import StateList

urlpatterns = [
    url(r'^country/(?P<pk>\d+)/$', StateList.as_view()),
]
