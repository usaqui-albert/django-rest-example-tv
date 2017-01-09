import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from helpers.tests_helpers import CustomTestCase
from posts.dashboard import views

pytestmark = pytest.mark.django_db


class AdminActiveDeactivePostView(CustomTestCase):

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', data={})
        resp = views.AdminActiveDeactivePostView.as_view()(req)
        assert resp.status_code == 401

    def test_get_request_not_allowed(self):
        req = self.factory.get('/', data={})
        resp = views.AdminActiveDeactivePostView.as_view()(req)
        assert resp.status_code == 401

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', data={})
        resp = views.AdminActiveDeactivePostView.as_view()(req)
        assert resp.status_code == 401

    def test_get_request_not_allowed_auth(self):
        user = self.load_users_data().get_user(is_staff=True)
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminActiveDeactivePostView.as_view()(req)
        assert resp.status_code == 405

    # def test_get_request_no_auth(self):
        # post = mixer.blend('posts.post')
    #     req = self.factory.get('/')
    #     awaited_message = 'Authentication credentials were not provided.'
    #     resp = views.AdminActiveDeactivePostView.as_view()(req)
    #     assert 'detail' in resp.data
    #     assert resp.data['detail'] == awaited_message
    #     assert resp.status_code == 401

    # def test_get_request_no_admin(self):
    #     user = self.load_users_data().get_user()
    #     req = self.factory.get('/')
    #     force_authenticate(req, user=user)
    #     resp = views.AdminActiveDeactivePostView.as_view()(req)
    #     assert 'detail' in resp.data
    #     assert resp.status_code == 403

    # def test_get_request_admin(self):
    #     user = self.load_users_data().get_user(is_staff=True)
    #     req = self.factory.get('/')
    #     force_authenticate(req, user=user)
    #     resp = views.AdminActiveDeactivePostView.as_view()(req)
    #     assert 'results' in resp.data
    #     assert resp.status_code == 200
