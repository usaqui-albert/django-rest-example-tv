import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from helpers.tests_helpers import CustomTestCase
from apptexts.dashboard import views

pytestmark = pytest.mark.django_db


class TestAdminAppTextView(CustomTestCase):

    def test_get_request_not_allowed(self):
        req = self.factory.get('/', data={})
        resp = views.AdminAppTextView.as_view()(req)
        assert resp.status_code == 401

    def test_get_request_success(self):
        user = self.load_users_data().get_user(is_staff=True)
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminAppTextView.as_view()(req)
        assert resp.status_code == 200

    def test_patch_request_not_admin(self):
        user = self.load_users_data().get_user(is_staff=False)
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminAppTextView.as_view()(req)
        assert resp.status_code == 403

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', data={})
        resp = views.AdminAppTextView.as_view()(req)
        assert resp.status_code == 401

    def test_post_request_not_allowed_auth(self):
        user = self.load_users_data().get_user(is_staff=False)
        req = self.factory.post('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminAppTextView.as_view()(req)
        assert resp.status_code == 403


class TestAdminAppTextDetailView(CustomTestCase):

    def test_get_request_not_allowed(self):
        req = self.factory.get('/', data={})
        resp = views.AdminAppTextDetailView.as_view()(req)
        assert resp.status_code == 401

    def test_get_request_success(self):
        user = self.load_users_data().get_user(is_staff=True)
        app_text = mixer.blend('apptexts.AppText')
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminAppTextDetailView.as_view()(req, pk=app_text.id)
        assert resp.status_code == 200

    def test_patch_request_not_admin(self):
        user = self.load_users_data().get_user(is_staff=False)
        req = self.factory.get('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminAppTextDetailView.as_view()(req)
        assert resp.status_code == 403

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', data={})
        resp = views.AdminAppTextDetailView.as_view()(req)
        assert resp.status_code == 401

    def test_post_request_not_allowed_auth(self):
        user = self.load_users_data().get_user(is_staff=False)
        req = self.factory.post('/', data={})
        force_authenticate(req, user=user)
        resp = views.AdminAppTextView.as_view()(req)
        assert resp.status_code == 403

    def test_patch_request_success(self):
        description = "BLAH"
        user = self.load_users_data().get_user(is_staff=True)
        app_text = mixer.blend('apptexts.AppText')
        req = self.factory.patch(
            '/',
            data={
                'description': description
            }
        )
        force_authenticate(req, user=user)
        resp = views.AdminAppTextDetailView.as_view()(req, pk=app_text.id)
        assert resp.status_code == 200
        assert resp.data['description'] == description

    def test_patch_request_bad_login(self):
        description = "BLAH"
        user = self.load_users_data().get_user(is_staff=False)
        app_text = mixer.blend('apptexts.AppText')
        req = self.factory.patch(
            '/',
            data={
                'description': description
            }
        )
        force_authenticate(req, user=user)
        resp = views.AdminAppTextDetailView.as_view()(req, pk=app_text.id)
        assert resp.status_code == 403
