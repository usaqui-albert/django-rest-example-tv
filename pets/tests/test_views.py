"""Testing Views"""
import pytest

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from .. import views
from .. import models

from users.models import User

pytestmark = pytest.mark.django_db


class TestPetListCreateView:
    factory = APIRequestFactory()

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 403, (
            'Should return Method Forbidden (403) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_get_request_no_admin(self):
        user = mixer.blend(User, is_staff=False)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 403, (
            'Should return OK (200) and a json response ' +
            'with a list of all users.')

    # def test_post_valid_data(self):
    #     data = {
    #         'email': 'john_doe@test.com',
    #         'password': 'a1234567',
    #         'full_name': 'John Doe',
    #         'username': 'JDoe'
    #     }
    #     req = self.factory.post('/', data=data)
    #     resp = views.PetsListCreateView.as_view()(req)
    #     assert resp.status_code == 201, (
    #         'Should return Created (201) and a json response with ' +
    #         'username, token, ful_name, groups, id and email'
    #     )

    # def test_post_invalid_data(self):
    #     data = {
    #         'email': 'john_doe@com',
    #         'password': 'a1234567',
    #         'full_name': 'John Doe',
    #         'username': 'JDoe'
    #     }
    #     req = self.factory.post('/', data=data)
    #     resp = views.PetsListCreateView.as_view()(req)
    #     assert resp.status_code == 400, (
    #         'Should return Bad Request (400) with an invalid email'
    #     )
