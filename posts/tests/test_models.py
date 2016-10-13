"""Testing models"""

import pytest

from mixer.backend.django import mixer
from django.core.management import call_command

pytestmark = pytest.mark.django_db


class TestPost:
    @staticmethod
    def loading_data():
        return call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)

    def get_user(self):
        self.loading_data()
        return mixer.blend('users.User', groups_id=1)

    def test_model(self):
        obj = mixer.blend('posts.Post', user=self.get_user())
        assert obj.pk == 1, 'Should create a Post instance'

    def test_is_paid_post_no_paid(self):
        obj = mixer.blend('posts.Post',
                          visible_by_owner=True,
                          visible_by_vet=False,
                          user=self.get_user())
        assert not obj.is_paid(), 'Should return False'

    def test_is_paid_post_paid(self):
        obj = mixer.blend('posts.Post',
                          visible_by_owner=True,
                          visible_by_vet=True,
                          user=self.get_user())
        assert obj.is_paid(), 'Should return True'

    def test_set_paid(self):
        obj = mixer.blend('posts.Post',
                          visible_by_owner=True,
                          visible_by_vet=False,
                          user=self.get_user())
        assert not obj.is_paid(), 'Should return False'
        obj.set_paid()
        assert obj.is_paid(), 'Should return True'
