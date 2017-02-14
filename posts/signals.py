from users.tasks import send_report
from activities.models import Activity
from TapVet.messages import liking_post
from TapVet.utils import send_notification_message


def post_reporting_signal(sender, instance=None, created=False, **kwargs):
    if created:
        send_report(instance.user, instance)


def new_post_like_signal(sender, instance=None, created=False, **kwargs):
    if created:
        post_owner = instance.post.user
        if post_owner.interested_notification:
            send_notification_message(post_owner.id, liking_post)

        Activity.objects.update_or_create(
            user=instance.user,
            action=Activity.LIKE,
            post=instance.post,
            defaults={'active': True}
        )


def inactive_post_like_signal(sender, instance=None, **kwargs):
    Activity.objects.update_or_create(
        user=instance.user,
        action=Activity.LIKE,
        post=instance.post,
        defaults={'active': False}
    )
