from django.conf.urls import url

from .views import StateListView, CountryListView

urlpatterns = [
    url(r'^country/(?P<pk>\d+)/states/$', StateListView.as_view()),
    url(r'^country/$', CountryListView.as_view()),
]
