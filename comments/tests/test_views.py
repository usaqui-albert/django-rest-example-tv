"""Testing Views"""
import pytest

from rest_framework.test import force_authenticate

from mixer.backend.django import mixer

from .. import views
from .. import models

from helpers.tests_helpers import CustomTestCase

pytestmark = pytest.mark.django_db


class TestCommentsPetOwnerListCreateView(CustomTestCase):

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.CommentsPetOwnerListCreateView.as_view()(req)
        assert resp.status_code == 403

    def test_request_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.CommentsPetOwnerListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_get_list(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        mixer.blend(models.Comment, post=post, user=user)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert len(resp.data) == 1

    def test_post_create(self):
        user = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.Post', user=user)
        data = {
            'description': 'BLAH BLAH'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.data['description'] == data['description']

    def test_get_list_no_pet_owner(self):
        user = self.load_users_data().get_user(groups_id=4)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        mixer.blend(models.Comment, post=post, user=user)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 403


class TestCommentsVetListCreateView(CustomTestCase):

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.CommentsVetListCreateView.as_view()(req)
        assert resp.status_code == 405

    def test_request_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.CommentsVetListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_get_list(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        mixer.blend(models.Comment, post=post, user=user)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.CommentsVetListCreateView.as_view()(req, pk=post.pk)
        assert len(resp.data) == 1

    def test_get_list_no_vet(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        mixer.blend(models.Comment, post=post, user=user)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.CommentsVetListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200

    def test_post_create(self):
        user = self.load_users_data().get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        data = {
            'description': 'BLAH BLAH'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.CommentsVetListCreateView.as_view()(req, pk=post.pk)
        assert resp.data['description'] == data['description']


class TestCommentVoteView(CustomTestCase):

    def test_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.CommentVoteView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.CommentVoteView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_get_vote_count(self):
        owner = self.load_users_data().get_user(groups_id=1)
        liker = self.get_user(groups_id=1)
        post = mixer.blend('posts.Post', user=owner)
        comment = mixer.blend(models.Comment, post=post, user=owner)
        req = self.factory.post('/')
        force_authenticate(req, user=liker)
        resp = views.CommentVoteView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 201
        # Now we test the counter
        req = self.factory.get('/')
        force_authenticate(req, user=owner)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.data[0]['upvoters_count'] == 1

    def test_get_downvote_count(self):
        owner = self.load_users_data().get_user(groups_id=1)
        liker1 = self.get_user(groups_id=1)
        liker2 = self.get_user(groups_id=1)
        post = mixer.blend('posts.Post', user=owner)
        comment = mixer.blend(models.Comment, post=post, user=owner)
        req = self.factory.post('/')
        force_authenticate(req, user=liker1)
        resp = views.CommentVoteView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 201
        force_authenticate(req, user=liker2)
        resp = views.CommentVoteView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 201
        # Now we test the counter
        req = self.factory.get('/')
        force_authenticate(req, user=owner)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.data[0]['upvoters_count'] == 2
        # Now test the downvote
        req = self.factory.delete('/')
        force_authenticate(req, user=liker1)
        resp = views.CommentVoteView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 204
        req = self.factory.get('/')
        force_authenticate(req, user=owner)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.data[0]['upvoters_count'] == 1
