"""Testing Views"""
import pytest
from PIL import Image
from django.test import RequestFactory

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer
from countries import models as models_c
from pets.models import get_current_year, get_limit_year
from helpers.tests_helpers import CustomTestCase

from posts.tests.test_views import get_test_image
from TapVet.images import STANDARD_SIZE, THUMBNAIL_SIZE

from .. import views
from .. import models


pytestmark = pytest.mark.django_db


class TestUserAuth(CustomTestCase):

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.UserAuth.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405) given the method ' +
            'does not exists'
        )

    def test_post_valid_data(self):
        user = self.load_users_data().get_user(groups_id=1)
        user.set_password('pass')
        user.save()
        data = {
            'username': user.username,
            'password': 'pass'
        }
        req = self.factory.post('/', data=data)

        resp = views.UserAuth.as_view()(req)
        for key in [
            'full_name', 'email', 'token', 'stripe_token', 'groups', 'id'
        ]:
            assert key in resp.data
        assert resp.status_code == 200, 'Should return Success (200)'

    def test_post_incomplete_data_password(self):
        data = {
            'username': 'JDoe',
        }
        req = self.factory.post('/', data=data)

        resp = views.UserAuth.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == (
            'Your username and password do not match.')
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_invalid_data(self):
        data = {
            'username': 'JDoe',
            'password': 'xxxxxxx',
        }
        req = self.factory.post('/', data=data)

        resp = views.UserAuth.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == (
            'Your username and password do not match.')
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_incomplete_data_username(self):
        data = {
            'password': 'a1234567',
        }
        req = self.factory.post('/', data=data)

        resp = views.UserAuth.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == (
            'Your username and password do not match.')
        assert resp.status_code == 400, 'Should return Bad Request (400)'


class TestUserView(CustomTestCase):

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', data={})
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_delete_request_not_allowed(self):
        req = self.factory.delete('/')
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        awaited_message = 'Authentication credentials were not provided.'

        resp = views.UserView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == awaited_message
        assert resp.status_code == 403, 'Should return Forbidden (403)'

    def test_get_request_with_authentication(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())
        resp = views.UserView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) and a json response ' +
            'with a list of all users.')

    def test_post_request_valid_data(self):
        self.load_users_data()
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        for key in ['full_name', 'email', 'token', 'username', 'groups', 'id']:
            assert key in resp.data
        assert resp.status_code == 201, 'Should return Created (201)'

    def test_post_request_wrong_format_email(self):
        self.load_users_data()
        data = {
            'email': 'john_doe@com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert 'email' in resp.data
        assert 'Enter a valid email address.' in resp.data['email']
        assert resp.status_code == 400, (
            'Should return Bad Request (400) with an invalid email'
        )

    def test_post_request_email_already_exists(self):
        user = self.load_users_data().get_user()
        data = {
            'email': user.email,
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)
        resp = views.UserView.as_view()(req)
        assert 'email' in resp.data
        assert 'user with this email already exists.' in resp.data['email']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_username_already_exists(self):
        user = self.load_users_data().get_user()
        data = {
            'email': 'asdas@asdas.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': user.username,
            'groups': 1
        }
        req = self.factory.post('/', data=data)

        resp = views.UserView.as_view()(req)
        assert 'username' in resp.data
        assert 'user with this username already ' \
               'exists.'in resp.data['username']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_username_field_missing(self):
        self.load_users_data()
        data = {
            'email': 'john_doe@gmail.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)

        resp = views.UserView.as_view()(req)
        assert 'username' in resp.data
        assert 'This field is required.' in resp.data['username']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_email_field_missing(self):
        self.load_users_data()
        data = {
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)

        resp = views.UserView.as_view()(req)
        assert 'email' in resp.data
        assert 'This field is required.' in resp.data['email']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_full_name_field_missing(self):
        self.load_users_data()
        data = {
            'email': 'john_doe@gmail.com',
            'password': 'a1234567',
            'username': 'JDoe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)

        resp = views.UserView.as_view()(req)
        assert 'full_name' in resp.data
        assert 'This field is required.' in resp.data['full_name']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_password_field_missing(self):
        self.load_users_data()
        data = {
            'email': 'john_doe@gmail.com',
            'full_name': 'John Doe',
            'username': 'JDoe',
            'groups': 1
        }
        req = self.factory.post('/', data=data)

        resp = views.UserView.as_view()(req)
        assert 'password' in resp.data
        assert 'This field is required.' in resp.data['password']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_groups_field_missing(self):
        data = {
            'email': 'john_doe@gmail.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        req = self.factory.post('/', data=data)

        resp = views.UserView.as_view()(req)
        assert 'groups' in resp.data
        assert 'This field is required.' in resp.data['groups']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_check_username_already_exists(self):
        self.get_user(username='jdoe')
        req = self.factory.get('/?username=jdoe')
        resp = views.UserView.as_view()(req)
        assert isinstance(resp.data, list) and len(resp.data) > 0
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_check_username_is_available(self):
        self.get_user(username='jdoe')
        req = self.factory.get('/?username=anotherjdoe')
        resp = views.UserView.as_view()(req)
        assert isinstance(resp.data, list) and len(resp.data) == 0
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_check_email_already_exists(self):
        self.get_user(email='jdoe@gmail.com')
        req = self.factory.get('/?email=jdoe@gmail.com')
        resp = views.UserView.as_view()(req)
        assert isinstance(resp.data, list) and len(resp.data) > 0
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_check_email_is_available(self):
        self.get_user(email='jdoe@gmail.com')
        req = self.factory.get('/?email=anotherjdoe@gmail.com')
        resp = views.UserView.as_view()(req)
        assert isinstance(resp.data, list) and len(resp.data) == 0
        assert resp.status_code == 200, 'Should return OK (200)'


class TestUserDetailView(CustomTestCase):

    def test_get_request_non_authenticated_user_and_does_not_exist(self):
        req = self.factory.get('/')
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=1)
        assert resp.status_code == 404, 'Should return Unauthorized (401)'

    def test_get_request_non_authenticated_user_and_object_exist(self):
        user = self.load_users_data().get_user()
        req = self.factory.get('/?owner=True')
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.id)
        assert resp.status_code == 200, 'Should return OK 200()'

    def test_get_request_non_authenticated_vet_and_object_exist(self):
        user = self.load_users_data().get_user()
        req = self.factory.get('/?vet=True')
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.id)
        assert resp.status_code == 200, 'Should return OK 200()'

    def test_get_request_non_authenticated_vet_and_no_query(self):
        user = self.load_users_data().get_user()
        req = self.factory.get('/')
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.id)
        assert resp.status_code == 400

    def test_get_request_with_authentication(self):
        user = self.load_users_data().get_user()
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_update_request_with_authentication(self):
        user = self.load_users_data().get_user(groups_id=2)
        data = {
            "full_name": "Albert Usaqui",
            "email": user.email,
        }
        req = self.factory.patch('/', data=data)
        force_authenticate(req, user=user)
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, (
            'Should return OK (200) given the data to update is valid')
        user.refresh_from_db()
        assert user.full_name == 'Albert Usaqui', 'Should update the user'

    def test_put_request_by_different_user(self):
        user = self.get_user()
        user2 = self.get_user()
        data = {
            "full_name": "Albert Usaqui",
            "email": user.email,
        }
        req = self.factory.patch('/', data=data)
        force_authenticate(req, user=user2)
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.pk)
        assert 'detail' in resp.data
        assert resp.status_code == 403, 'Should return HTTP 403 Forbidden'
        assert resp.data['detail'] == ('You do not have permission to perform '
                                       'this action.')

    def test_delete_request_authenticated_but_no_admin(self):
        req = self.factory.delete('/')
        force_authenticate(req, user=self.get_user())
        resp = views.UserRetrieveUpdateView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'You need admin status to delete.'
        assert resp.status_code == 401, (
            'Should return HTTP 401 Unauthorized')

    def test_delete_request_only_admin_allowed(self):
        user = self.get_user(is_staff=True)
        req = self.factory.delete('/')
        force_authenticate(req, user=user)
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.pk)
        assert resp.status_code == 204, 'Should return No Content (204)'

    def test_update_with_image(self):
        user = self.load_users_data().get_user(groups_id=2)
        tmp_file = get_test_image()
        data = {
            "full_name": "Albert Usaqui",
            "email": user.email,
            'image': tmp_file
        }
        tmp_file.seek(0)
        req = self.factory.patch('/', data=data)
        force_authenticate(req, user=user)
        resp = views.UserRetrieveUpdateView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200, (
            'Should return OK (200) given the data to update is valid')
        user.refresh_from_db()
        assert user.full_name == 'Albert Usaqui', 'Should update the user'
        img_s = Image.open(user.image.standard)
        img_t = Image.open(user.image.thumbnail)
        assert img_s.size == STANDARD_SIZE
        assert img_t.size == THUMBNAIL_SIZE


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
        user.refresh_from_db()
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


class TestVeterinarianListCreateView(CustomTestCase):

    def test_get_request(self):
        user = self.load_users_data().get_user()
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
        user = self.load_users_data().get_user()
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': 1989,
            'veterinarian_type': 5,
            'area_interest': 'dogs'

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return error, dogs its no area of interest'
        )

    def test_post_request(self):
        user = self.load_users_data().get_user(groups_id=4)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() - 5,
            'veterinarian_type': 5,
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

    def test_post_request_bad_year(self):
        user = self.load_users_data().get_user(groups_id=4)

        user = mixer.blend(models.User, groups_id=4)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_limit_year() - 10,
            'veterinarian_type': '4',
            'area_interest': area_interest.pk,
            'country': country.id,
            'state': state.id
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return HTTP 400 Bad Request, bad year'
        )

    def test_post_request_bad_year_high(self):
        user = self.load_users_data().get_user(groups_id=4)
        user = mixer.blend(models.User, groups_id=4)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() + 22,
            'veterinarian_type': 4,
            'area_interest': area_interest.pk,
            'country': country.id,
            'state': state.id
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return HTTP 400 Bad Request, bad year'
        )

    def test_post_request_no_country_student(self):
        user = self.load_users_data().get_user(groups_id=4)
        user = mixer.blend(models.User, groups_id=4)
        area_interest = mixer.blend(models.AreaInterest)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() - 10,
            'veterinarian_type': '4',
            'area_interest': area_interest.pk,
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return object created (201)'
        )

    def test_post_request_no_country_vet(self):
        user = self.load_users_data().get_user(groups_id=3)
        area_interest = mixer.blend(models.AreaInterest)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() - 10,
            'veterinarian_type': '3',
            'area_interest': area_interest.pk,
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return HTTP 400 Bad Request'
        )

    def test_post_request_empty(self):
        user = self.load_users_data().get_user(groups_id=5)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'This field <veterinary_school, graduating_year,' +
            ' veterinarian_type, area_interest> is required'
        )

    def test_post_request_bad_type(self):
        user = self.load_users_data().get_user(groups_id=3)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() - 10,
            'veterinarian_type': 'other',
            'area_interest': 'dogs'

        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return HTTP 400 Bad Request'
        )

    def test_post_request_bad_state_no_exists(self):
        user = self.load_users_data().get_user(groups_id=4)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() - 11,
            'veterinarian_type': 'vet',
            'area_interest': area_interest.id,
            'country': country.id,
            'state': 100
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)

        assert resp.status_code == 400, (
            'Should return HTTP 400 Bad Request'
        )

    def test_post_request_bad_state(self):
        user = self.load_users_data().get_user(groups_id=5)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State)
        data = {
            'veterinary_school': 'CharField',
            'graduating_year': get_current_year() - 5,
            'veterinarian_type': 'vet',
            'area_interest': area_interest.id,
            'country': country.id,
            'state': state.id
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.VeterinarianListCreateView.as_view()(req)
        assert resp.status_code == 400, (
            'Should return HTTP 400 Bad Request'
        )


class TestAreaInterestListView(CustomTestCase):
    factory = RequestFactory()

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.AreaInterestListView.as_view()(req)
        assert resp.status_code == 401, (
            'Authentication credentials were not provided')

    def test_get_request(self):
        user = self.load_users_data().get_user()
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.AreaInterestListView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return OK (200) with the list of all Area of interest')

    def test_post_request(self):
        user = self.get_user()
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.AreaInterestListView.as_view()(req)
        assert resp.status_code == 405, (
            '"detail": "Method "POST" not allowed."')


class TestUserFollowView(CustomTestCase):

    def test_request_no_auth(self):
        req = self.factory.post('/')
        resp = views.UserFollowView.as_view()(req)
        assert resp.status_code == 401, 'Should return Unauthorized (401)'

    def test_request_no_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.UserFollowView.as_view()(req)
        assert resp.status_code == 405

    def test_pet_owner_follow_vet(self):
        pet_owner = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=4)
        req = self.factory.post('/')
        force_authenticate(req, user=pet_owner)
        resp = views.UserFollowView.as_view()(req, pk=vet.pk)
        assert resp.status_code == 403

    def test_vet_follow_pet_owner(self):
        pet_owner = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=4)
        req = self.factory.post('/')
        force_authenticate(req, user=vet)
        resp = views.UserFollowView.as_view()(req, pk=pet_owner.pk)
        assert resp.status_code == 403

    def test_vet_follow_vet(self):
        vet = self.load_users_data().get_user(groups_id=3)
        vet1 = self.get_user(groups_id=3)
        area_interest = mixer.blend(models.AreaInterest)
        country = mixer.blend(models_c.Country)
        state = mixer.blend(models_c.State, country=country)
        data = {
            'graduating_year': get_current_year() - 5,
            'veterinarian_type': 5,
            'area_interest': area_interest,
            'country': country,
            'state': state,
            'veterinarian_type': '3'
        }
        mixer.blend('users.Veterinarian', user=vet, verified=True, **data)
        mixer.blend('users.Veterinarian', user=vet1, verified=True, **data)
        req = self.factory.post('/')
        force_authenticate(req, user=vet)
        resp = views.UserFollowView.as_view()(req, pk=vet1.pk)
        assert resp.status_code == 201

    def test_pet_owner_follow_pet_owner(self):
        pet_owner = self.load_users_data().get_user(groups_id=1)
        pet_owner1 = self.get_user(groups_id=2)
        req = self.factory.post('/')
        force_authenticate(req, user=pet_owner)
        resp = views.UserFollowView.as_view()(req, pk=pet_owner1.pk)
        assert resp.status_code == 201

    def test_vet_unfollow_vet(self):
        vet = self.load_users_data().get_user(groups_id=3)
        vet1 = self.get_user(groups_id=4)
        req = self.factory.delete('/')
        force_authenticate(req, user=vet)
        resp = views.UserFollowView.as_view()(req, pk=vet1.pk)
        assert resp.status_code == 204

    def test_pet_owner_unfollow_pet_owner(self):
        pet_owner = self.load_users_data().get_user(groups_id=3)
        pet_owner1 = self.get_user(groups_id=4)
        req = self.factory.delete('/')
        force_authenticate(req, user=pet_owner)
        resp = views.UserFollowView.as_view()(req, pk=pet_owner1.pk)
        assert resp.status_code == 204

    def test_no_vet_yet_follow(self):
        vet = self.load_users_data().get_user(groups_id=3)
        vet1 = self.get_user(groups_id=4)
        req = self.factory.post('/')
        force_authenticate(req, user=vet)
        resp = views.UserFollowView.as_view()(req, pk=vet1.pk)
        assert resp.status_code == 403


class TestUserFeedBackView(CustomTestCase):

    def test_request_no_auth(self):
        req = self.factory.post('/')
        resp = views.UserFeedBackView.as_view()(req)
        assert resp.status_code == 401, 'Should return Unauthorized (401)'

    def test_request_no_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.UserFeedBackView.as_view()(req)
        assert resp.status_code == 405

    def test_request_post_complete(self):
        data = {
            'message': 'Blah Blah'
        }
        req = self.factory.post('/', data)
        force_authenticate(req, user=self.get_user())
        resp = views.UserFeedBackView.as_view()(req)
        assert resp.status_code == 204


class TestReferFriendView(CustomTestCase):

    def test_get_request_not_allowed(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())
        resp = views.ReferFriendView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "GET" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)'
        )

    def test_put_request_not_allowed(self):
        req = self.factory.put('/')
        force_authenticate(req, user=self.get_user())
        resp = views.ReferFriendView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "PUT" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)'
        )

    def test_delete_request_not_allowed(self):
        req = self.factory.delete('/')
        force_authenticate(req, user=self.get_user())
        resp = views.ReferFriendView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "DELETE" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)'
        )

    def test_post_request_user_no_authenticated(self):
        req = self.factory.post('/')
        resp = views.ReferFriendView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 401
        assert resp.data['detail'] == (
            'Authentication credentials were not provided.'
        )

    def test_post_request_email_field_missing(self):
        req = self.factory.post('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.ReferFriendView.as_view()(req)
        assert 'email' in resp.data
        assert resp.status_code == 400, 'Should return Bad Request (400)'
        assert 'This field is required.' in resp.data['email']

    def test_post_request_empty_email(self):
        data = {'email': ''}
        req = self.factory.post('/', data)
        force_authenticate(req, user=self.get_user())
        resp = views.ReferFriendView.as_view()(req)
        assert 'email' in resp.data
        assert 'This field may not be blank.' in resp.data['email']
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_request_wrong_format_email(self):
        data = {'email': 'jdoe@gmail.c'}
        req = self.factory.post('/', data)
        force_authenticate(req, user=self.get_user())
        resp = views.ReferFriendView.as_view()(req)
        assert 'email' in resp.data
        assert 'Enter a valid email address.' in resp.data['email']
        assert resp.status_code == 400, 'Should return Bad Request (400)'


class TestUserFollowsListView(CustomTestCase):

    def test_request_not_allowed(self):
        req = self.factory.post('/')
        force_authenticate(req, user=self.get_user())
        resp = views.UserFollowsListView.as_view()(req)
        assert resp.data['detail'] == 'Method "POST" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)'
        )

    def test_request_no_auth(self):
        to_follow = self.load_users_data().get_user(groups_id=1)
        user = self.get_user(groups_id=1)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.UserFollowView.as_view()(req, pk=to_follow.pk)
        assert resp.status_code == 201
        req = self.factory.get('/')
        resp = views.UserFollowsListView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1
        for key in [
            'username', 'email', 'full_name', 'groups', 'id', 'image', 'label',
            
        ]:
            assert key in resp.data['results'][0]

    def test_get_list(self):
        to_follow = self.load_users_data().get_user(groups_id=1)
        user = self.get_user(groups_id=1)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.UserFollowView.as_view()(req, pk=to_follow.pk)
        assert resp.status_code == 201
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.UserFollowsListView.as_view()(req, pk=user.pk)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1
        for key in [
            'username', 'email', 'full_name', 'groups', 'id', 'image', 'label',
            'following'
        ]:
            assert key in resp.data['results'][0]
        assert resp.data['results'][0]['following']


class TestUserFollowedListView(CustomTestCase):

    def test_request_not_allowed(self):
        req = self.factory.post('/')
        force_authenticate(req, user=self.get_user())
        resp = views.UserFollowedListView.as_view()(req)
        assert resp.data['detail'] == 'Method "POST" not allowed.'
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)'
        )

    def test_request_no_auth(self):
        to_follow = self.load_users_data().get_user(groups_id=1)
        user = self.get_user(groups_id=1)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.UserFollowView.as_view()(
            req, pk=to_follow.pk)
        assert resp.status_code == 201
        req = self.factory.get('/')
        resp = views.UserFollowedListView.as_view()(req, pk=to_follow.pk)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1
        for key in [
            'username', 'email', 'full_name', 'groups', 'id', 'image', 'label',
        ]:
            assert key in resp.data['results'][0]
        assert resp.data['results'][0]['id'] == user.id

    def test_get_list(self):
        to_follow = self.load_users_data().get_user(groups_id=1)
        user = self.get_user(groups_id=1)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.UserFollowView.as_view()(
            req, pk=to_follow.pk)
        assert resp.status_code == 201
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.UserFollowedListView.as_view()(req, pk=to_follow.pk)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1
        for key in [
            'username', 'email', 'full_name', 'groups', 'id', 'image', 'label',
            'following'
        ]:
            assert key in resp.data['results'][0]
        assert resp.data['results'][0]['id'] == user.id


class TestUserDeactive(CustomTestCase):

    def test_no_auth(self):
        req = self.factory.delete('')
        resp = views.UserDeactive.as_view()(req)
        assert resp.status_code == 401

    def test_method_not_allowed(self):
        user = self.get_user(groups_id=1)
        req = self.factory.post('/')
        force_authenticate(req, user=user)
        resp = views.UserDeactive.as_view()(req)
        assert resp.status_code == 405

    def test_method_allowed(self):
        user = self.get_user(groups_id=1)
        req = self.factory.delete('/')
        force_authenticate(req, user=user)
        resp = views.UserDeactive.as_view()(req)
        assert resp.status_code == 204

    def test_delete_staff(self):
        user = self.get_user(is_staff=True)
        req = self.factory.delete('/')
        force_authenticate(req, user=user)
        resp = views.UserDeactive.as_view()(req)
        assert resp.status_code == 403

    def test_delete_superadmin(self):
        user = self.get_user(is_superuser=True)
        req = self.factory.delete('/')
        force_authenticate(req, user=user)
        resp = views.UserDeactive.as_view()(req)
        assert resp.status_code == 403
