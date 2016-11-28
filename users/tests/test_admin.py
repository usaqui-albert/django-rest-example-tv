import pytest

from helpers.tests_helpers import CustomTestCase
from users.dashboard import views

pytestmark = pytest.mark.django_db


class TestAdminUserAuth(CustomTestCase):

    def test_get_request(self):
        req = self.factory.get('/')
        resp = views.AdminAuth.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405) given the method ' +
            'does not exists'
        )

    def test_post_valid_data_no_admin(self):
        user = self.load_users_data().get_user(groups_id=1)
        user.set_password('pass')
        user.save()
        data = {
            'username': user.username,
            'password': 'pass'
        }
        req = self.factory.post('/', data=data)

        resp = views.AdminAuth.as_view()(req)
        assert resp.status_code == 400

    def test_post_valid_data(self):
        user = self.load_users_data().get_user(groups_id=6)
        user.set_password('pass')
        user.is_staff = True
        user.save()
        data = {
            'username': user.username,
            'password': 'pass'
        }
        req = self.factory.post('/', data=data)
        resp = views.AdminAuth.as_view()(req)
        assert resp.status_code == 200, 'Should return Success (200)'
        for key in [
            'id', 'full_name', 'email', 'groups',
            'created_at', 'stripe_token', 'image',
            'label', 'token', 'settings', 'created_at'
        ]:
            assert key in resp.data

    def test_post_incomplete_data_password(self):
        data = {
            'username': 'JDoe',
        }
        req = self.factory.post('/', data=data)

        resp = views.AdminAuth.as_view()(req)
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

        resp = views.AdminAuth.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == (
            'Your username and password do not match.')
        assert resp.status_code == 400, 'Should return Bad Request (400)'

    def test_post_incomplete_data_username(self):
        data = {
            'password': 'a1234567',
        }
        req = self.factory.post('/', data=data)

        resp = views.AdminAuth.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == (
            'Your username and password do not match.')
        assert resp.status_code == 400, 'Should return Bad Request (400)'
