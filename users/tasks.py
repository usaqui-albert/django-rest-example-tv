from django.conf import settings

import sendgrid
from sendgrid.helpers.mail import (
    Email,
    Mail,
    Personalization,
    Substitution
)


def refer_a_friend_by_email(receiver_email, sender_user):
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(
                sender_user,
                to_mail=receiver_email
            ),
            template=settings.SENDGRID_REFER_FRIEND
        )
    )


def welcome_mail(user, group=None):
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(user),
            template=settings.SENDGRID_WELCOME.get(group)
        )
    )


def password_reset(user, verification_code):
    substitutions = [Substitution('-code-', verification_code)]
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(user, substitutions),
            template=settings.SENDGRID_PASSWORD_RESET
        )
    )


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
        )
    )


def send_feedback(user, message):
    substitutions = [Substitution('-message-', message.encode('utf-8'))]
    mails = [
        Email(email=admin[1], name=admin[0]) for admin in settings.ADMINS
    ]
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(
                user, substitutions, to_mails=mails),
            template=settings.SENDGRID_FEEDBACK
        )
    )


def send_report(user, report):
    substitutions = [
        Substitution('-post-', report.post.id),
        Substitution('-type-', report.get_type_display()),
        Substitution('-post_message-', report.post.description.encode('utf-8'))
    ]
    mails = [
        Email(email=admin[1], name=admin[0]) for admin in settings.ADMINS
    ]
    sendgrid_api(
        obtain_mail(
            personalization=obtain_personalization(
                user, substitutions, to_mails=mails),
            template=settings.SENDGRID_REPORT
        )
    )


def obtain_personalization(
    user, substitutions=None, to_mails=None, to_mail=None
):
    personalization = Personalization()

    if to_mail:
        personalization.add_to(Email(to_mail))
    else:
        personalization.add_to(Email(user.email))

    personalization.add_substitution(Substitution('-name-', user.full_name))
    personalization.add_substitution(Substitution('-username-', user.username))
    personalization.add_substitution(Substitution('-email-', user.email))
    if substitutions:
        for substitution in substitutions:
            personalization.add_substitution(substitution)
    if to_mails:
        for mail in to_mails:
            personalization.add_to(mail)
    return personalization


def obtain_mail(personalization, template):
    mail = Mail()
    mail.set_template_id(template)
    mail.set_from(Email(settings.DEFAULT_FROM_EMAIL, 'TapVet Team'))
    mail.add_personalization(personalization)
    return mail.get()


def sendgrid_api(mail):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    if settings.SEND_MAILS:
        sg.client.mail.send.post(
            request_body=mail
        )
