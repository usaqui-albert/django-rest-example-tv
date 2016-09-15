"""Testing Views"""
import pytest

from django.test import RequestFactory
from mixer.backend.django import mixer

from countries import models as models_c
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
        assert resp.status_code == 200, (
            'Should return Success (200) with all valid parameters'
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


class TestUserView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.UserCreateView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405) given ' +
            'the method does not exists'
        )

    def test_post_valid_data(self):
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserCreateView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return Created (201) with all valid parameters'
        )

    def test_post_invalid_data(self):
        data = {
            'email': 'john_doe@com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserCreateView.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with an invalid email'
        )


class TestUserDetailView:
    factory = RequestFactory()

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        resp = views.UserDetailView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_update_request(self):
        user = mixer.blend(models.User)
        req = self.factory.put('/', data={'full_name': 'Albert Usaqui'})
        resp = views.UserDetailView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, (
            'Should return OK (200) given the data to update is valid')
        user.refresh_from_db()
        assert user.full_name == 'Albert Usaqui', 'Should update the user'


class GroupsListView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.GroupsListView.as_view()(req)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_post_request(self):
        req = self.factory.post('/')
        resp = views.GroupsListView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method \"POST\" not allowed."')


class UserListView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.UserListView.as_view()(req)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_post_request(self):
        req = self.factory.post('/')
        resp = views.UserListView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method \"POST\" not allowed."')


class TestBreederListCreateView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.BreederListCreateView.as_view()(req)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_post_request(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'user': user.id,
            'breeder_type': 'CharField',
            'bussiness_name': 'CharField',
            'country': country.id,
            'state': state.id

        }
        req = self.factory.post('/', data=data)
        resp = views.BreederListCreateView.as_view()(req)
        # import ipdb; ipdb.set_trace()
        print resp.data
        assert resp.status_code == 201, (
            'Should return Created (201) with all valid parameters'
        )


class TestVeterinarianListCreateView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.VeterinarianListCreateView.as_view()(req)
        assert resp.status_code == 200, 'Should return OK (200)'
