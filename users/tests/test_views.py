"""Testing serializers"""

import pytest

from mixer.backend.django import mixer
from django.test import RequestFactory
from .. import views
from .. import models

pytestmark = pytest.mark.django_db


class TestUserView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 405, 'Should return status code 405(Method not allowed)'

    def test_post_valid_data(self):
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 201, 'Should return status code 201(Created)'

    def test_post_invalid_data(self):
        data = {
            'email': 'john_doe@com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 400, 'Should return status code 400(Bad request)'


class TestUserDetailView:
    factory = RequestFactory()

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        resp = views.UserDetailView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, 'Should return status code 200(OK)'

    def test_update_request(self):
        user = mixer.blend(models.User)
        req = self.factory.put('/', data={'full_name': 'Albert Usaqui'})
        resp = views.UserDetailView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, (
            'Should return status code 200(OK) given the data to update is valid')
        user.refresh_from_db()
        assert user.full_name == 'Albert Usaqui', 'Should update the user'
