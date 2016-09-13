import pytest

from django.test import RequestFactory
from mixer.backend.django import mixer
from django.contrib.auth.hashers import make_password
from .. import views
from .. import models

pytestmark = pytest.mark.django_db


class TestUserAuth:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.UserAuth.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405) given the method ' +
            'does not exists'
        )

    def test_post_valid_data(self):
        user = mixer.blend(models.User)
        user.set_password('pass')
        user.save()
        data = {
            'username': user.username,
            'password': 'pass'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserAuth.as_view()(req)
        # import ipdb; ipdb.set_trace()
        assert resp.status_code == 200, (
            'Should return Success (200) with all valid parameters'
        )

    def test_post_invalid_data(self):
        data = {
            'username': 'JDoe',
            'password': 'xxxxxxx',
        }
        req = self.factory.post('/', data=data)
        resp = views.UserAuth.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with ' +
            '{"non_field_errors":["Unable to log in with provided ' +
            'credentials."]}'
        )

    def test_post_incomplete_data_username(self):
        data = {
            'password': 'a1234567',
        }
        req = self.factory.post('/', data=data)
        resp = views.UserAuth.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with ' +
            '{"username":["This field is required."]}'
        )

    def test_post_incomplete_data_password(self):
        data = {
            'username': 'JDoe',
        }
        req = self.factory.post('/', data=data)
        resp = views.UserAuth.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with ' +
            '{"password":["This field is required."]}'
        )
