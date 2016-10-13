"""Testing models"""

import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestPost:
    def test_model(self):
        obj = mixer.blend('posts.Post')
        assert obj.pk == 1, 'Should create a Post instance'

    def test_is_paid_post_no_paid(self):
        obj = mixer.blend(
            'posts.Post',
            visible_by_owner=True,
            visible_by_vet=False)
        assert not obj.is_paid(), 'Should return False'

    def test_is_paid_post_paid(self):
        obj = mixer.blend(
            'posts.Post',
            visible_by_owner=True,
            visible_by_vet=True)
        assert obj.is_paid(), 'Should return True'

    def test_set_paid(self):
        obj = mixer.blend(
            'posts.Post',
            visible_by_owner=True,
            visible_by_vet=False)
        assert not obj.is_paid(), 'Should return False'
        obj.set_paid()
        assert obj.is_paid(), 'Should return True'
