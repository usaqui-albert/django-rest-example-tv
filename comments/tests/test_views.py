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
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'Method "PUT" not allowed.'
        assert resp.status_code == 405, ('Should return Method Not Allowed '
                                         '(405)')

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=1)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_get_list(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        mixer.blend(models.Comment, post=post, user=user)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert len(resp.data['results']) == 1
        for key in [
            'description', 'id', 'post', 'created_at', 'updated_at',
            'upvoters_count', 'label', 'full_name', 'upvoted', 'user'
        ]:
            assert key in resp.data['results'][0]
        assert resp.data['results'][0]['full_name'] == user.full_name

    def test_post_create(self):
        user = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.Post', user=user, visible_by_vet=False)
        data = {
            'description': 'BLAH BLAH'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 201
        assert resp.data['description'] == data['description']

    def test_post_create_vet_comment(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user, visible_by_vet=False)
        data = {
            'description': 'BLAH BLAH'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=vet)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 403

    def test_get_list_no_pet_owner(self):
        vet = self.load_users_data().get_user(groups_id=4)
        post = mixer.blend('posts.Post', user=vet)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=vet)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 200, 'Should return OK (200)'


class TestCommentsVetListCreateView(CustomTestCase):

    def test_put_request_not_allowed(self):
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user())
        resp = views.CommentsVetListCreateView.as_view()(req)
        assert resp.status_code == 405

    def test_get_request_no_auth(self):
        req = self.factory.get('/')
        resp = views.CommentsVetListCreateView.as_view()(req, pk=1)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_get_list(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user)
        mixer.blend(models.Comment, post=post, user=user)
        mixer.blend(models.Comment, post=post, user=vet)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.CommentsVetListCreateView.as_view()(req, pk=post.pk)
        assert len(resp.data['results']) == 1
        for key in [
            'description', 'id', 'post', 'created_at', 'updated_at',
            'upvoters_count', 'label', 'full_name', 'upvoted'
        ]:
            assert key in resp.data['results'][0]
        assert resp.data[
            'results'][0]['full_name'] == 'Veterinary Professional #%s' % (
                1000 + vet.id
        )

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
        assert resp.status_code == 201
        assert resp.data['description'] == data['description']

    def test_post_create_vet_comment(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user, visible_by_vet=True)
        data = {
            'description': 'BLAH BLAH'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=vet)
        resp = views.CommentsVetListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 201
        assert resp.data['description'] == data['description']

    def test_post_create_vet_comment_no_paid(self):
        user = self.load_users_data().get_user(groups_id=1)
        vet = self.get_user(groups_id=5)
        post = mixer.blend('posts.Post', user=user, visible_by_vet=False)
        data = {
            'description': 'BLAH BLAH'
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=vet)
        resp = views.CommentsVetListCreateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 403


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
        assert resp.data['results'][0]['upvoters_count'] == 1

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
        assert resp.data['results'][0]['upvoters_count'] == 2
        # Now test the downvote
        req = self.factory.delete('/')
        force_authenticate(req, user=liker1)
        resp = views.CommentVoteView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 204
        req = self.factory.get('/')
        force_authenticate(req, user=owner)
        resp = views.CommentsPetOwnerListCreateView.as_view()(req, pk=post.pk)
        assert resp.data['results'][0]['upvoters_count'] == 1


class TestFeedbackCreateView(CustomTestCase):

    def test_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.FeedbackCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_get(self):
        user = self.get_user()
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.FeedbackCreateView.as_view()(req)
        assert resp.status_code == 405

    def test_post(self):
        user = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', user=user)
        comment = mixer.blend('comments.comment', post=post)
        data = {
            'description': 'blah blah',
            'was_helpful': True
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.FeedbackCreateView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 201
        assert resp.data['was_helpful']

    def test_post_bad(self):
        user = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post')
        comment = mixer.blend('comments.comment', post=post)
        data = {
            'description': 'blah blah',
            'was_helpful': True
        }
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.FeedbackCreateView.as_view()(req, pk=comment.pk)
        assert resp.status_code == 403
