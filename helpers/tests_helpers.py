from django.core.management import call_command
from django.utils import timezone
from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory


class CustomTestCase:

    factory = APIRequestFactory()

    def load_users_data(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)
        return self

    def load_countries_data(self):
        call_command(
            'loaddata', '../../countries/fixtures/countries.json', verbosity=0)
        return self

    def load_feed_variables(self):
        call_command(
            'loaddata', '../../posts/fixtures/posts.json', verbosity=0)
        return self

    @staticmethod
    def get_user(**kwargs):
        return mixer.blend('users.User', **kwargs)

    @staticmethod
    def get_current_year():
        return timezone.now().year
