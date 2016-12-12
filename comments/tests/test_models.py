"""Testing Models"""
import pytest

from mixer.backend.django import mixer

from .. import models

from helpers.tests_helpers import CustomTestCase

pytestmark = pytest.mark.django_db


class TestFeedbackModel(CustomTestCase):

    def test_feedback_model(self):
        user = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', user=user)
        comment = mixer.blend('comments.comment', post=post)
        feedback = models.Feedback(
            comment=comment,
            user=user,
            was_helpful=True,
            description='Blah blah'
        )
        feedback.save()
        assert feedback.was_helpful

    def test_feedback_model_bad(self):
        user = self.load_users_data().get_user(groups_id=1)
        user_comment = self.load_users_data().get_user(groups_id=1)
        post = mixer.blend('posts.post', user=user)
        comment = mixer.blend('comments.comment', post=post)
        feedback = models.Feedback(
            comment=comment,
            user=user_comment,
            was_helpful=True,
            description='Blah blah'
        )
        try:
            feedback.save()
        except ValueError as e:
            assert str(e) == (
                'Error: the user have to be the same that the post owner')
