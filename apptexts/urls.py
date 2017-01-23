from django.conf.urls import url

from .views import AppTextView, AppTextDetailView


urlpatterns = [
    url(r'^$', AppTextView.as_view()),
    url(r'^(?P<pk>\d+)/$', AppTextDetailView.as_view()),

]
