from django.core.mail import EmailMessage
from rest_framework.authtoken.models import Token
from django.conf import settings


def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def new_breeder_signal(sender, instance=None, created=False, **kwargs):
    if created:
        message_title = (getattr(
            settings, 'EMAIL_SUBJECT_PREFIX', None) +
            getattr(settings, 'BREADER_MESSAGE_ADMIN_TITLE', None))
        message_body = 'There is a need breeder registration.'
        email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        email = EmailMessage(
            subject=message_title,
            body=message_body,
            from_email=email_from,
            to=[admin_email],
            reply_to=[email_from],
        )
        email.content_subtype = "html"
        email.send()


def new_vet_signal(sender, instance=None, created=False, **kwargs):
    if created:
        message_title = (getattr(
            settings, 'EMAIL_SUBJECT_PREFIX', None) +
            getattr(settings, 'VET_MESSAGE_ADMIN_TITLE', None))
        message_body = 'There is a need vet registration.'
        email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        email = EmailMessage(
            subject=message_title,
            body=message_body,
            from_email=email_from,
            to=[admin_email],
            reply_to=[email_from],
        )
        email.content_subtype = "html"
        email.send()
