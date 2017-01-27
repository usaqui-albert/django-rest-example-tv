from django.core.mail import mail_admins
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

from celery.task import task

import sendgrid
from sendgrid.helpers.mail import (
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
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(user),
            template=settings.SENDGRID_WELCOME.get(group)
        ))


@task(ignore_result=True)
def password_reset(user, verification_code):
    substitutions = [Substitution('-code-', verification_code)]
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(user, substitutions),
            template=settings.SENDGRID_PASSWORD_RESET
        ))


@task(ignore_result=True)
def vet_verify_mail(user, veterinarian_type):
    template = ''
    if veterinarian_type == 3:
        template = settings.SENDGRID_VALIDATED.get('VETERINARIAN')
    else:
        template = settings.SENDGRID_VALIDATED.get('TECHNICIAN_STUDENT')
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(user),
            template=template
        ))


def obtain_personalization(user, substitutions=None):
    personalization = Personalization()
    personalization.add_to(Email(user.email))
    personalization.add_substitution(Substitution('-name-', user.full_name))
    personalization.add_substitution(Substitution('-username-', user.username))
    personalization.add_substitution(Substitution('-email-', user.email))
    if substitutions:
        for substitution in substitutions:
            personalization.add_substitution(substitution)
    return personalization


def obtain_mail(personalization, template):
    mail = Mail()
    mail.set_template_id(template)
    mail.set_from(Email(settings.DEFAULT_FROM_EMAIL, 'Tapvet Team'))
    mail.add_personalization(personalization)
    return mail.get()


def sendgrid_api(mail):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    sg.client.mail.send.post(
        request_body=mail
    )
