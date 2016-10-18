from django.core.management import call_command
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

    @staticmethod
    def get_user(**kwargs):
        return mixer.blend('users.User', **kwargs)
