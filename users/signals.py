from django.core.mail import mail_admins
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.template.loader import render_to_string


def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def new_breeder_signal(sender, instance=None, created=False, **kwargs):
    if created:
        message_title = getattr(settings, 'BREADER_MESSAGE_ADMIN_TITLE', None)
        message_body = 'There is a need breeder registration.'
        msg_html = render_to_string(
            'users/partials/email/breeder.html', {'breeder': instance})
        mail_admins(
            subject=message_title, message=message_body, fail_silently=True,
            html_message=msg_html)


def new_vet_signal(sender, instance=None, created=False, **kwargs):
    if created:
        message_title = getattr(settings, 'VET_MESSAGE_ADMIN_TITLE', None)
        message_body = 'There is a need vet registration.'
        msg_html = render_to_string(
            'users/partials/email/vet.html', {'vet': instance})
        mail_admins(
            subject=message_title, message=message_body, fail_silently=True,
            html_message=msg_html)
