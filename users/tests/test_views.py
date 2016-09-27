"""Testing Views"""
import pytest

from django.test import RequestFactory


from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

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
            'Should return Success (200) with a json with: token ' +
            'id, full_name, and email'
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

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 403, (
            'Should return Method Forbidden (403) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_post_valid_data(self):
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return Created (201) and a json response with ' +
            'username, token, ful_name, groups, id and email'
        )

    def test_post_invalid_data(self):
        data = {
            'email': 'john_doe@com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with an invalid email'
        )

    def test_post_data_duplicate(self):
        user = mixer.blend(models.User)
        data = {
            'email': user.email,
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 400, (
            'Should return Bad Request (400) user with this email ' +
            'already exists.'
        )

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) and a json response ' +
            'with a list of all users.')


class TestUserDetailView:
    factory = APIRequestFactory()

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.UserGetUpdateView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_update_request(self):
        user = mixer.blend(models.User)
        data = {
            "full_name": "Albert Usaqui",
            "email": user.email,
        }
        req = self.factory.patch('/', data=data)
        force_authenticate(req, user=user)
        resp = views.UserGetUpdateView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, (
            'Should return OK (200) given the data to update is valid')
        user.refresh_from_db()
        assert user.full_name == 'Albert Usaqui', 'Should update the user'


class GroupsListView:
    factory = RequestFactory()

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.GroupsListView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200), with the list of the groups')

    def test_post_request(self):
        req = self.factory.post('/')
        resp = views.GroupsListView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')


class TestBreederListCreateView:
    factory = RequestFactory()

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.BreederListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) with the list of all breeders')

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.BreederListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Authentication credentials were not provided')

    def test_post_request(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'breeder_type': 'CharField',
            'business_name': 'CharField',
            'country': country.id,
            'state': state.id

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.BreederListCreateView.as_view()(req)

        assert resp.status_code == 201, (
            'Should return Created (201) with all valid parameters'
        )

    def test_post_request_bad_state(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        country2 = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'breeder_type': 'CharField',
            'business_name': 'CharField',
            'country': country2.id,
            'state': state.id

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.BreederListCreateView.as_view()(req)
        assert resp.status_code == 400, (
            'The state provided is not from the country provided'
        )

    def test_post_request_empty(self):
        user = mixer.blend(models.User)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.BreederListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'This field <country, state, business_name, breeder_type>' +
            ' is required'
        )

    def test_post_request_bad_country(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'breeder_type': 'CharField',
            'business_name': 'CharField',
            'country': 100,
            'state': state.id

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.BreederListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Invalid pk 100 - object does not exist'
        )

    def test_post_request_bad_state_no_exists(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        data = {
            'breeder_type': 'CharField',
            'business_name': 'CharField',
            'country': country.id,
            'state': 100
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.BreederListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Invalid pk 100 - object does not exist'
        )


class TestVeterinarianListCreateView:
    factory = RequestFactory()

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) with the list of all veterinarians')

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.VeterinarianListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Authentication credentials were not provided')

    def test_post_request_bad(self):
        user = mixer.blend(models.User)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': 1989,
            'veterinarian_type': 'tech',
            'area_interest': 'dogs'

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return error, dogs its no area of interest'
        )

    def test_post_request(self):
        user = mixer.blend(models.User)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': 1989,
            'veterinarian_type': 'tech',
            'area_interest': area_interest.pk,
            'country': country.id,
            'state': state.id
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 201, (
            'Should return object created (201)'
        )

    def test_post_request_empty(self):
        user = mixer.blend(models.User)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'This field <veterinary_school, graduating_year,' +
            ' veterinarian_type, area_interest> is required'
        )

    def test_post_request_bad_type(self):
        user = mixer.blend(models.User)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': 1989,
            'veterinarian_type': 'other',
            'area_interest': 'dogs'

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Invalid pk 100 - object does not exist'
        )

    def test_post_request_bad_state_no_exists(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        data = {
            'breeder_type': 'CharField',
            'business_name': 'CharField',
            'country': country.id,
            'state': 100
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Invalid pk 100 - object does not exist'
        )


class TestAuthorizeBreederView:
    factory = APIRequestFactory()

    def test_post_request(self):
        user = mixer.blend(models.User, is_staff=True)
        req = self.factory.post('/')
        force_authenticate(req, user)
        resp = views.AuthorizeBreederView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')

    def test_get_request(self):
        req = self.factory.get('/')
        user = mixer.blend(models.User, is_staff=True)
        force_authenticate(req, user)
        resp = views.AuthorizeBreederView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')

    def test_post_request_no_admin(self):
        user = mixer.blend(models.User)
        req = self.factory.post('/')
        force_authenticate(req, user)
        resp = views.AuthorizeBreederView.as_view()(req)
        assert resp.status_code == 403, (
            '"detail": "Forbidden. No access to non admin user"')

    def test_get_request_no_admin(self):
        req = self.factory.get('/')
        user = mixer.blend(models.User)
        force_authenticate(req, user)
        resp = views.AuthorizeBreederView.as_view()(req)
        assert resp.status_code == 403, (
            '"detail": "Forbidden.  No access to non admin user"')

    def test_patch_request(self):
        user = mixer.blend(models.User, is_staff=True)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        breeder = mixer.blend(models.Breeder, country=country, state=state)
        req = self.factory.patch('/', data={'verified': "True"})
        force_authenticate(req, user=user)
        resp = views.AuthorizeBreederView.as_view()(req, pk=breeder.pk)
        assert resp.status_code == 202, (
            'Should return all 202 and the breeder with verified field true')

    def test_patch_request_no_admin(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        breeder = mixer.blend(models.Breeder, country=country, state=state)
        req = self.factory.patch('/', data={'verified': "True"})
        force_authenticate(req, user=user)
        resp = views.AuthorizeBreederView.as_view()(req, pk=breeder.pk)
        assert resp.status_code == 403, (
            '"detail": "Forbidden.  No access to non admin user"')


class TestAuthorizeVetView:
    factory = APIRequestFactory()

    def test_get_request(self):
        user = mixer.blend(models.User, is_staff=True)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.AuthorizeVetView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')

    def test_post_request(self):
        user = mixer.blend(models.User, is_staff=True)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.AuthorizeVetView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')

    def test_patch_request(self):
        user = mixer.blend(models.User, is_staff=True)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        vet = mixer.blend(models.Veterinarian, country=country, state=state)
        req = self.factory.patch('/', data={'verified': "True"})
        force_authenticate(req, user=user)
        resp = views.AuthorizeVetView.as_view()(req, pk=vet.pk)
        assert resp.status_code == 202, (
            'Should return all 202 and the vet with verified field true')

    def test_patch_request_no_admin(self):
        user = mixer.blend(models.User)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        vet = mixer.blend(models.Veterinarian, country=country, state=state)
        req = self.factory.patch('/', data={'verified': "True"})
        force_authenticate(req, user=user)
        resp = views.AuthorizeVetView.as_view()(req, pk=vet.pk)
        assert resp.status_code == 403, (
            '"detail": "Forbidden.  No access to non admin user"')


class TestAreaInterestListView:
    factory = RequestFactory()

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.AreaInterestListView.as_view()(req)
        assert resp.status_code == 401, (
            'Authentication credentials were not provided')

    def test_get_request(self):
        user = mixer.blend(models.User)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.AreaInterestListView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) with the list of all Area of interest')

    def test_post_request(self):
        user = mixer.blend(models.User)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.AreaInterestListView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')
