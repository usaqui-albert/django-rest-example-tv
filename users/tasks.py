from celery.task import task

from django.core.mail import mail_admins
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings


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
