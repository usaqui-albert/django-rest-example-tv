"""Testing Views"""
import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from .. import views
from .. import models
from helpers.tests_helpers import CustomTestCase

pytestmark = pytest.mark.django_db


class TestPetListCreateView(CustomTestCase):

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())

        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "PUT" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_delete_request_not_allowed(self):
        req = self.factory.delete('/')
        force_authenticate(req, user=self.get_user())

        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "DELETE" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_get_request_user_no_authenticated(self):
        req = self.factory.get('/')
        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Authentication credentials were ' \
                                      'not provided.'
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401)')

    def test_get_request_user_authenticated_but_no_admin(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())
        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Admin level is needed for this action.'
        assert resp.status_code == 403, (
            'Should return Method Forbidden (403)')

    def test_get_request_user_authenticated_and_admin(self):
        user = self.get_user(is_staff=True)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) and a json response ' +
            'with a list of all pets.')

    def test_post_valid_data(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        awaited_keys = ['name', 'gender', 'image', 'breed', 'image_url',
                        'user', 'pet_type', 'fixed', 'id', 'birth_year']
        for key in awaited_keys:
            assert key in resp.data
        assert resp.status_code == 201, 'Should return Created (201)'

    def test_post_request_birth_year_101_years_ago(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': self.get_current_year() - 101,
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'The pet year of birth cannot be ' \
                                      'lower than 1916'
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_birth_year_into_the_future(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        next_year = self.get_current_year() + 1
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': next_year,
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data)
        force_authenticate(req, user=user)

        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'The pet year of birth cannot be ' \
                                      'higher than the current year'
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_birth_year_field_missing(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data)
        force_authenticate(req, user=user)

        resp = views.PetsListCreateView.as_view()(req)
        assert 'birth_year' in resp.data
        assert 'This field is required.' in resp.data['birth_year']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_birth_year_empty_field(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data)
        force_authenticate(req, user=user)

        resp = views.PetsListCreateView.as_view()(req)
        assert 'birth_year' in resp.data
        assert 'A valid integer is required.' in resp.data['birth_year']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_name_field_missing(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'fixed': 'True',
            'birth_year': self.get_current_year() - 1,
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data)
        force_authenticate(req, user=user)

        resp = views.PetsListCreateView.as_view()(req)
        assert 'name' in resp.data
        assert 'This field is required.' in resp.data['name']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_name_empty_field(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': '',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'name' in resp.data
        assert 'This field may not be blank.' in resp.data['name']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_pet_type_field_missing(self):
        user = self.load_users_data().get_user(groups_id=1)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': self.get_current_year() - 1,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data)
        force_authenticate(req, user=user)

        resp = views.PetsListCreateView.as_view()(req)
        assert 'pet_type' in resp.data
        assert 'This field is required.' in resp.data['pet_type']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_pet_type_empty_field(self):
        user = self.load_users_data().get_user(groups_id=1)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': '',
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'pet_type' in resp.data
        assert 'This field may not be null.' in resp.data['pet_type']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_pet_type_does_not_exists(self):
        user = self.load_users_data().get_user(groups_id=1)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': 1,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'pet_type' in resp.data
        assert 'Invalid pk "1" - object does ' \
               'not exist.' in resp.data['pet_type']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_pet_type_wrong_data_type_value(self):
        user = self.load_users_data().get_user(groups_id=1)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': 'some string',
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'pet_type' in resp.data
        assert 'Incorrect type. Expected pk value, ' \
               'received unicode.' in resp.data['pet_type']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_gender_field_missing(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'gender' in resp.data
        assert 'This field is required.' in resp.data['gender']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_gender_invalid_choice(self):
        user = self.load_users_data().get_user(groups_id=1)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'any choice'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'gender' in resp.data
        assert '"any choice" is not a valid choice.' in resp.data['gender']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_valid_data_invalid_group(self):
        user = self.get_user(group_id=3)
        pet_type = mixer.blend(models.PetType)
        data = {
            'name': 'John Doe',
            'fixed': 'True',
            'birth_year': '2016',
            'pet_type': pet_type.id,
            'breed': 'Labrator',
            'gender': 'male',
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PetsListCreateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'This user doesn\'t have pets.'
        assert resp.status_code == 401, 'Should return Unauthorized (401)'


class TestPetTypeListView(CustomTestCase):

    def test_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.PetTypeListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Authentication credentials ' \
                                      'were not provided.'
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401)')

    def test_post_no_auth(self):
        req = self.factory.post('/')
        resp = views.PetTypeListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Authentication credentials ' \
                                      'were not provided.'
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401)')

    def test_get(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())
        resp = views.PetTypeListView.as_view()(req)
        assert resp.status_code == 200, (
            'Should  return HTTP 200 OK, with a list of pet types')

    def test_post_request_not_allowed(self):
        req = self.factory.post('/')
        force_authenticate(req, user=self.get_user())
        resp = views.PetTypeListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "POST" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405) given the method ' +
            'does not exists'
        )

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.PetTypeListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "PUT" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_delete_request_not_allowed(self):
        req = self.factory.delete('/')
        force_authenticate(req, user=self.get_user())
        resp = views.PetTypeListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "DELETE" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')
