from rest_framework.authentication import TokenAuthentication as TokenAuth

from rest_framework import exceptions


class TokenAuthentication(TokenAuth):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related(
                'user__groups'
            ).get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)
