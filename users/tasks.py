from django.core.mail import mail_admins
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

from celery.task import task

import sendgrid
from sendgrid.helpers.mail import (
    Content,
    Email,
    Mail,
    Personalization,
    Substitution
)


@task(ignore_result=True)
def send_mail(subject, message, html_message, fail_silently=True):
    mail_admins(
        subject=subject, message=message, fail_silently=fail_silently,
        html_message=html_message
    )


@task(ignore_result=True)
def refer_a_friend_by_email(receiver, sender_user):
    subject = 'Awesome! %s has invited you to check out TapVet' % sender_user
    from_email = settings.EMAIL_HOST_USER
    to = receiver
    htmly = get_template('users/partials/email/email_to_refer.html')
    d = Context({'full_name': sender_user})
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, '', from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@task(ignore_result=True)
def welcome_mail(user, group=None):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    mail = Mail()
    mail.set_template_id(settings.SENDGRID_WELCOME.get(group))
    mail.set_from(Email(settings.DEFAULT_FROM_EMAIL, 'Tapvet Team'))
    personalization = Personalization()
    personalization.add_to(Email(user.email))
    personalization.set_subject(
        settings.EMAIL_SUBJECT_PREFIX + ' Welcome -username-')
    mail.add_content(Content("text/plain", 'hello'))
    mail.add_content(Content("text/html", 'hello'))
    personalization.add_substitution(Substitution('-name-', user.full_name))
    personalization.add_substitution(Substitution('-username-', user.username))
    personalization.add_substitution(Substitution('-email-', user.email))
    mail.add_personalization(personalization)
    sg.client.mail.send.post(request_body=mail.get())


@task(ignore_result=True)
def password_reset(user, verification_code):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    mail = Mail()
    mail.set_template_id(settings.SENDGRID_PASSWORD_RESET)
    mail.set_from(Email(settings.DEFAULT_FROM_EMAIL, 'Tapvet Team'))
    personalization = Personalization()
    personalization.add_to(Email(user.email))
    personalization.set_subject(
        settings.EMAIL_SUBJECT_PREFIX + ' Password Reset -username-')
    mail.add_content(Content("text/plain", 'hello'))
    mail.add_content(Content("text/html", 'hello'))
    personalization.add_substitution(Substitution('-name-', user.full_name))
    personalization.add_substitution(Substitution('-code-', verification_code))
    personalization.add_substitution(Substitution('-username-', user.username))
    personalization.add_substitution(Substitution('-email-', user.email))
    mail.add_personalization(personalization)
    sg.client.mail.send.post(request_body=mail.get())


@task(ignore_result=True)
def vet_verify_mail(user, veterinarian_type):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    mail = Mail()

    if veterinarian_type == 3:
        mail.set_template_id(
            settings.SENDGRID_VALIDATED.get('VETERINARIAN')
        )

    else:
        mail.set_template_id(
            settings.SENDGRID_VALIDATED.get('TECHNICIAN_STUDENT')
        )

    mail.set_from(Email(settings.DEFAULT_FROM_EMAIL, 'Tapvet Team'))
    personalization = Personalization()
    personalization.add_to(Email(user.email))
    personalization.set_subject(
        settings.EMAIL_SUBJECT_PREFIX + ' Password Reset -username-')
    mail.add_content(Content("text/plain", 'hello'))
    mail.add_content(Content("text/html", 'hello'))
    personalization.add_substitution(Substitution('-name-', user.full_name))
    personalization.add_substitution(Substitution('-username-', user.username))
    personalization.add_substitution(Substitution('-email-', user.email))
    mail.add_personalization(personalization)
    sg.client.mail.send.post(request_body=mail.get())
