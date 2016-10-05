from celery.task import task
from django.core.mail import mail_admins


@task(ignore_result=True)
def send_mail(subject, message, html_message, fail_silently=True):
    mail_admins(
        subject=subject, message=message, fail_silently=fail_silently,
        html_message=html_message
    )
