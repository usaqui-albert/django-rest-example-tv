from django.conf import settings
from django.template.loader import render_to_string

from users.tasks import send_mail
from activities.models import Activity


def post_reporting_signal(sender, instance=None, created=False, **kwargs):
    if created:
        message_title = getattr(settings, 'REPORT_MESSAGE_ADMIN_TITLE', None)
        message_body = 'There is a new post reported'
        msg_html = render_to_string(
            'posts/email/report_a_post.html',
            {
                'full_name': instance.user.full_name,
                'report_type': instance.get_type_as_string()
            }
        )
        send_mail.delay(
            message_title, message_body, msg_html, True)


def new_post_like_signal(sender, instance=None, created=False, **kwargs):
    if created:
        activity = Activity(
            user=instance.user,
            action=Activity.LIKE,
            post=instance.post
        )
        activity.save()
