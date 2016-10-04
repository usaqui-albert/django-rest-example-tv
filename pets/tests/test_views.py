"""Testing Views"""
import pytest
from django.core.management import call_command

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
            'Should return Method Unauthorized (401) with a json ' +
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
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        user = mixer.blend(User, groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'john doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return Created (201) and a json response with ' +
            'name, fixed, birth_year, pet_type, breed, gender')

    def test_post_invalid_data(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        user = mixer.blend(User, groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'john doe',
            'fixed': 'True',
            'birth_year': '16',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with an error:' +
            'The pet birth_year cannot be lower than 1916'
        )

    def test_post_valid_data_invalid_group(self):
        user = mixer.blend(User, group_id=3)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'john doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Unauthorized (401) and a json response with ' +
            'This user doesn\'t have pets')


class TestPetTypeListView:
    factory = APIRequestFactory()

    def test_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.PetTypeListView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_post_no_auth(self):
        req = self.factory.post('/')
        resp = views.PetTypeListView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_get(self):
        user = mixer.blend(User)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PetTypeListView.as_view()(req)
        assert resp.status_code == 200, (
            'Should  return HTTP 200 OK, with a list of pet types')

    def test_post(self):
        user = mixer.blend(User)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.PetTypeListView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405) given the method ' +
            'does not exists'
        )
