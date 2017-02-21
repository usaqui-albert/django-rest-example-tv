import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from helpers.tests_helpers import CustomTestCase
from posts.dashboard import views

pytestmark = pytest.mark.django_db


class TestAdminPostDetailView(CustomTestCase):

    def test_get_request_not_allowed(self):
        req = self.factory.get('/', data={})
        resp = views.AdminPostDetailView.as_view()(req)
        assert resp.status_code == 401

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', data={})
        resp = views.AdminPostDetailView.as_view()(req)
        assert resp.status_code == 401

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', data={})
        resp = views.AdminPostDetailView.as_view()(req)
        assert resp.status_code == 401

    def test_get_request_success(self):
        user = self.load_users_data().get_user(is_staff=True)
        post = mixer.blend('posts.Post')
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.id)
        assert resp.status_code == 200

    def test_patch_request_not_admin(self):
        user = self.load_users_data().get_user(is_staff=False)
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req)
        assert resp.status_code == 403

    def test_patch_request_admin_active_false(self):
        user = self.load_users_data().get_user(is_staff=True)
        post = mixer.blend('posts.post', active=True)
        req = self.factory.patch('/', data={'active': False})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200
        assert not resp.data['active']
        post.refresh_from_db()
        assert not post.active

    def test_patch_request_admin_active_true(self):
        user = self.load_users_data().get_user(is_staff=True)
        post = mixer.blend('posts.post', active=False)
        req = self.factory.patch('/', data={'active': True})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200
        assert resp.data['active']
        post.refresh_from_db()
        assert post.active
