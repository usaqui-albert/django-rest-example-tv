from django.conf.urls import url


from .views import (
    AdminAuth
)

urlpatterns = [
    url(r'^login/$', AdminAuth.as_view()),
]
