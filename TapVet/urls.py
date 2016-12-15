"""TapVet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from posts.views import PaymentAmountDetail

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(
        r'^api/v1/dashboard/users/',
        include('users.dashboard.urls', namespace='dashboard_users')
    ),
    url(
        r'^api/v1/dashboard/posts/',
        include('posts.dashboard.urls', namespace='dashboard_posts')
    ),
    url(r'^api/v1/users/', include('users.urls', namespace='users')),
    url(r'^api/v1/pets/', include('pets.urls', namespace='pets')),
    url(r'^api/v1/posts/', include('posts.urls', namespace='posts')),
    url(
        r'^api/v1/countries/',
        include('countries.urls', namespace='countries')
    ),
    url(r'^api/v1/comments/', include('comments.urls', namespace='comments')),
    url(
        r'^api/v1/configurations/prices/(?P<pk>[0-9]+)/$',
        PaymentAmountDetail.as_view()
    ),
    url(r'^docs/', include('rest_framework_docs.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
