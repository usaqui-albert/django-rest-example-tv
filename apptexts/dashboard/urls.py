from django.conf.urls import url

from .views import AdminAppTextView, AdminAppTextDetailView


urlpatterns = [
    url(r'^$', AdminAppTextView.as_view()),
    url(r'^(?P<pk>\d+)/$', AdminAppTextDetailView.as_view()),

]
