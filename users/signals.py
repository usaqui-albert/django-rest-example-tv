from rest_framework.authtoken.models import Token
from django.conf import settings
from django.template.loader import render_to_string

from .tasks import send_mail


def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def new_breeder_signal(sender, instance=None, created=False, **kwargs):
    if created:
        message_title = getattr(settings, 'BREADER_MESSAGE_ADMIN_TITLE', None)
        message_body = 'There is a need breeder registration.'
        msg_html = render_to_string(
            'users/partials/email/breeder.html', {'breeder': instance})
        send_mail.delay(
            message_title, message_body, msg_html, True)


def new_vet_signal(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.veterinarian_type == '4':
            instance.verified = True
            instance.save()
        message_title = getattr(settings, 'VET_MESSAGE_ADMIN_TITLE', None)
        message_body = 'There is a need vet registration.'
        msg_html = render_to_string(
            'users/partials/email/vet.html', {'vet': instance})
        send_mail.delay(
            message_title, message_body, msg_html, True)
