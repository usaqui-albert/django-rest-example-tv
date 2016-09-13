# testing serializers

import pytest
from .. import serializers

pytestmark = pytest.mark.django_db


class TestCreateUserSerializer:
    def test_serializer_no_data_given(self):
        serializer = serializers.CreateUserSerializer(data={})
        assert serializer.is_valid() is False, (
            'Should be invalid if no data is given')

    def test_serializer_empty_email(self):
        data = {
            'email': '',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is False and 'email' in serializer.errors, (
            'Should be invalid if the email field is empty'
        )

    def test_serializer_wrong_format_email(self):
        data = {
            'email': 'john_doe@com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is False and 'email' in serializer.errors, (
            'Should be invalid if the format email is wrong'
        )

    def test_serializer_right_format_email(self):
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is True, 'Should be valid if email format is right'

    def test_serializer_full_name_too_short(self):
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is False and 'full_name' in serializer.errors, (
            'Should be invalid if fullname is not long enough'
        )

    def test_serializer_full_name_long_enough(self):
        data = {
            'email': 'john_doe@test.com',
            'password': 'a1234567',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is True, 'Should be valid if fullname is long enough'

    def test_serializer_password_too_short(self):
        data = {
            'email': 'john_doe@test.com',
            'password': '123',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is False and 'password' in serializer.errors, (
            'Should be invalid if password is not long enough'
        )

    def test_serializer_password_long_enough(self):
        data = {
            'email': 'john_doe@test.com',
            'password': '12345678',
            'full_name': 'John Doe',
            'username': 'JDoe'
        }
        serializer = serializers.CreateUserSerializer(data=data)
        assert serializer.is_valid() is True, 'Should be valid if password is long enough'
