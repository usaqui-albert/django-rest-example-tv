from django.conf.urls import url

from .views import AppTextView


urlpatterns = [
    url(r'^$', AppTextView.as_view()),
]
