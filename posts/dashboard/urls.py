from django.conf.urls import url

from .views import AdminPostView


urlpatterns = [
    url(r'^$', AdminPostView.as_view()),
]
