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
        assert resp.status_code == 401, (
            'Should return Method UNAUTHORIZED (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_get_request_no_admin(self):
        user = mixer.blend(User, is_staff=False)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 403, (
            'Should return Method Forbidden (403) with a json ' +
            '"detail": "Admin level is needed for this action."')

    def test_get_request_admin(self):
        user = mixer.blend(User, is_staff=True)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) and a json response ' +
            'with a list of all pets.')

    def test_post_valid_data(self):
        user = mixer.blend(User)
        data = {
            'name': 'john doe',
            'fixed': 'True',
            'age': '2016',
            'pet_type': 'dog',
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return Created (201) and a json response with ' +
            'name, fixed, age, pet_type, breed, gender')

    def test_post_invalid_data(self):
        user = mixer.blend(User)
        data = {
            'name': 'john doe',
            'fixed': 'True',
            'age': '16',
            'pet_type': 'dog',
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with an error:' +
            'The pet age cannot be lower than 1916'
        )
