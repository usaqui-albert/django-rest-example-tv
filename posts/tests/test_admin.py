import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from helpers.tests_helpers import CustomTestCase
from activities.models import Activity

from posts.dashboard import views
from posts import views as posts_views

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

    def test_activities_no_deactive_error(self):
        # Like a post
        liker = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', active=True, visible_by_vet=False)
        req = self.factory.post('/')
        force_authenticate(req, user=liker)
        resp = posts_views.PostVoteView.as_view()(req, pk=post.pk)
        # Editing a post on admin
        user = self.load_users_data().get_user(is_staff=True)
        req = self.factory.patch('/', data={'visible_by_vet': 'true'})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200
        post.refresh_from_db()
        assert post.visible_by_vet
        assert Activity.objects.filter(post=post, active=True).count() == 1
        assert Activity.objects.first().active

    def test_activities_deactive(self):
        # Like a post
        liker = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', active=True)
        req = self.factory.post('/')
        force_authenticate(req, user=liker)
        resp = posts_views.PostVoteView.as_view()(req, pk=post.pk)
        # Deactive a post will deactive the Activities
        user = self.load_users_data().get_user(is_staff=True)
        req = self.factory.patch('/', data={'active': 'false'})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200
        assert Activity.objects.filter(post=post, active=True).count() == 0
        assert not Activity.objects.first().active

    def test_activities_reactive(self):
        # Like a post
        liker = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', active=True)
        req = self.factory.post('/')
        force_authenticate(req, user=liker)
        resp = posts_views.PostVoteView.as_view()(req, pk=post.pk)
        # Deactive a post will deactive the Activities
        user = self.load_users_data().get_user(is_staff=True)
        req = self.factory.patch('/', data={'active': 'false'})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200
        assert Activity.objects.filter(post=post, active=True).count() == 0
        assert not Activity.objects.first().active
        # Reactve the post and the activities
        user = self.load_users_data().get_user(is_staff=True)
        req = self.factory.patch('/', data={'active': 'true'})
        force_authenticate(req, user=user)
        resp = views.AdminPostDetailView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200
        assert Activity.objects.filter(post=post, active=True).count() == 1
        assert Activity.objects.first().active
