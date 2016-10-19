"""Testing models"""

import pytest

from mixer.backend.django import mixer

from pets.models import get_current_year
from helpers.tests_helpers import CustomTestCase

pytestmark = pytest.mark.django_db


class TestPost(CustomTestCase):

    def test_create_post_instance(self):
        user = self.load_users_data().get_user(groups_id=1)
        obj = mixer.blend('posts.Post', user=user)
        assert obj.pk == 1, 'Should create a Post instance'

    def test_is_paid_post_no_paid(self):
        user = self.load_users_data().get_user(groups_id=1)
        obj = mixer.blend('posts.Post',
                          visible_by_owner=True,
                          visible_by_vet=False,
                          user=user)
        assert not obj.is_paid(), 'Should return False'

    def test_is_paid_post_paid(self):
        user = self.load_users_data().get_user(groups_id=1)
        obj = mixer.blend('posts.Post',
                          visible_by_owner=True,
                          visible_by_vet=True,
                          user=user)
        assert obj.is_paid(), 'Should return True'

    def test_set_paid(self):
        user = self.load_users_data().get_user(groups_id=1)
        obj = mixer.blend('posts.Post',
                          visible_by_owner=True,
                          visible_by_vet=False,
                          user=user)
        assert not obj.is_paid(), 'Should return False'
        obj.set_paid()
        assert obj.is_paid(), 'Should return True'

    def test_post_if_vet_no_verified(self):
        user = self.load_users_data().get_user(groups_id=3)
        obj = mixer.blend('posts.post', user=user)
        assert not obj.visible_by_vet
        assert not obj.visible_by_owner

    def test_post_if_vet_verified(self):
        user = self.load_users_data().get_user(groups_id=3)
        country = mixer.blend('countries.country')
        state = mixer.blend('countries.state', country=country)
        mixer.blend(
            'users.veterinarian', user=user, verified=True,
            graduating_year=get_current_year() - 11,
            country=country, state=state)
        obj = mixer.blend('posts.post', user=user)
        assert obj.visible_by_vet
        assert not obj.visible_by_owner

    def test_post_if_student(self):
        user = self.load_users_data().get_user(groups_id=3)
        country = mixer.blend('countries.country')
        state = mixer.blend('countries.state', country=country)
        mixer.blend(
            'users.veterinarian', user=user, verified=True,
            graduating_year=get_current_year() - 11,
            country=country, state=state)
        obj = mixer.blend('posts.post', user=user)
        assert obj.visible_by_vet
        assert not obj.visible_by_owner

    def test_post_if_pet_owner(self):
        user = self.load_users_data().get_user(groups_id=1)
        obj = mixer.blend('posts.post', user=user)
        assert not obj.visible_by_vet
        assert obj.visible_by_owner

    def test_post_if_pet_owner_and_paid(self):
        user = self.load_users_data().get_user(groups_id=1)
        obj = mixer.blend('posts.post', user=user)
        obj.set_paid()
        assert obj.visible_by_vet
        assert obj.visible_by_owner
