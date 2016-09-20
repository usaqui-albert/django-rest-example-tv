from django.conf.urls import url

from .views import StateListView, CountryListView

urlpatterns = [
    url(r'^(?P<pk>\d+)/states/$', StateListView.as_view()),
    url(r'^$', CountryListView.as_view()),
]
