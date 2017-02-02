"""Testing Admin"""
import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from helpers.tests_helpers import CustomTestCase

from comments.dashboard import views

pytestmark = pytest.mark.django_db


class TestAdminFeedbackListView(CustomTestCase):

    def test_put_request_admin_not_allowed(self):
        req = self.factory.put('/', {})
        user = self.load_users_data().get_user(is_staff=True, groups_id=6)
        force_authenticate(req, user=user)
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 405

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        user = self.load_users_data().get_user(groups_id=6)
        force_authenticate(req, user=user)
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', {})
        user = self.load_users_data().get_user(is_staff=False)
        force_authenticate(req, user=user)
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_get_not_allowed(self):
        req = self.factory.get('/')
        user = self.load_users_data().get_user(is_staff=False)
        force_authenticate(req, user=user)
        resp = views.AdminFeedbackListView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_get_allowed(self):
        req = self.factory.get('/')
        user = self.load_users_data().get_user(is_staff=True)
        force_authenticate(req, user=user)
        resp = views.AdminFeedbackListView.as_view()(req)
        assert resp.status_code == 200


class TestAdminFeedbackView(CustomTestCase):

    def test_put_request_admin_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user(is_staff=True))
        resp = views.AdminFeedbackView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 405

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.AdminFeedbackView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_post_request_not_allowed(self):
        req = self.factory.post('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.AdminFeedbackView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_get_not_allowed(self):
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())
        resp = views.AdminFeedbackView.as_view()(req)
        assert 'detail' in resp.data
        assert resp.status_code == 403

    def test_get_allowed(self):
        req = self.factory.get('/')
        user = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', user=user)
        comment = mixer.blend('comments.comment', post=post)
        feedback = mixer.blend('comments.feedback', comment=comment, user=user)
        force_authenticate(req, user=self.get_user(is_staff=True))
        resp = views.AdminFeedbackView.as_view()(req, pk=feedback.pk)
        assert resp.status_code == 200
