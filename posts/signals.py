from users.tasks import send_report
from activities.models import Activity
from TapVet.messages import liking_post
from TapVet.utils import send_notification_message


def post_reporting_signal(sender, instance=None, created=False, **kwargs):
    if created:
        send_report(instance.user, instance)


def new_post_like_signal(sender, instance=None, created=False, **kwargs):
    if created:
        post_owner_id = instance.post.user_id
        send_notification_message(post_owner_id, liking_post)

        activity = Activity(
            user=instance.user,
            action=Activity.LIKE,
            post=instance.post
        )
        activity.save()
