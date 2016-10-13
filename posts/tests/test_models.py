"""Testing models"""
import pytest

from django.core.management import call_command

from mixer.backend.django import mixer

from pets.models import get_current_year

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

    def test_post_if_vet_no_verified(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        user = mixer.blend('users.user', groups_id=3)
        obj = mixer.blend('posts.post', user=user)
        assert not obj.visible_by_vet
        assert not obj.visible_by_owner

    def test_post_if_vet_verified(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        call_command(
            'loaddata', '../../countries/fixtures/countries.json', verbosity=0)
        user = mixer.blend('users.user', groups_id=3)
        mixer.blend(
            'users.veterinarian', user=user, verified=True,
            graduating_year=get_current_year() - 11,
            country_id=1, state_id=2)
        obj = mixer.blend('posts.post', user=user)
        assert obj.visible_by_vet
        assert not obj.visible_by_owner

    def test_post_if_student(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        call_command(
            'loaddata', '../../countries/fixtures/countries.json', verbosity=0)
        user = mixer.blend('users.user', groups_id=3)
        mixer.blend(
            'users.veterinarian', user=user, verified=True,
            graduating_year=get_current_year() - 11,
            country_id=1, state_id=2)
        obj = mixer.blend('posts.post', user=user)
        assert obj.visible_by_vet
        assert not obj.visible_by_owner

    def test_post_if_pet_owner(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        user = mixer.blend('users.user', groups_id=1)
        obj = mixer.blend('posts.post', user=user)
        assert not obj.visible_by_vet
        assert obj.visible_by_owner

    def test_post_if_pet_owner_and_paid(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        user = mixer.blend('users.user', groups_id=1)
        obj = mixer.blend('posts.post', user=user)
        obj.set_paid()
        assert obj.visible_by_vet
        assert obj.visible_by_owner
