from users.tasks import send_report
from activities.models import Activity


def post_reporting_signal(sender, instance=None, created=False, **kwargs):
    if created:
        send_report(instance.user, instance)


def new_post_like_signal(sender, instance=None, created=False, **kwargs):
    if created:
        activity = Activity(
            user=instance.user,
            action=Activity.LIKE,
            post=instance.post
        )
        activity.save()
