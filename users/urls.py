from django.conf.urls import url

from .views import UserAuth

urlpatterns = [
    url(r'^login/$', UserAuth.as_view()),
]
