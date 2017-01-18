"""Testing Admin"""
import pytest

from rest_framework.test import force_authenticate

from helpers.tests_helpers import CustomTestCase

from comments.dashboard import views

pytestmark = pytest.mark.django_db


class TestAdminFeedbackListView(CustomTestCase):

    def test_put_request_admin_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user(is_staff=True))
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 405

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_get_not_allowed(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_get_allowed(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user(is_staff=True))
        resp = views.AdminFeedbackListView.as_view()(req)
        assert resp.status_code == 200
