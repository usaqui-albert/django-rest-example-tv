from TapVet.utils import send_notification_message
from activities.models import Activity
from TapVet.messages import commenting_post


def new_comment_signal(sender, instance=None, created=False, **kwargs):
    if created:
        post_owner_id = instance.post.user_id
        send_notification_message(post_owner_id, commenting_post)

        activity = Activity(
            user=instance.user,
            action=Activity.COMMENT,
            post=instance.post,
            comment=instance
        )
        activity.save()


def upvoters_changed(sender, action=None, pk_set=None, **kwargs):
    if action == 'post_add':
        activity = Activity(
            user_id=pk_set.pop(),
            action=Activity.UPVOTE,
            comment=kwargs['instance'],
            post=kwargs['instance'].post
        )
        activity.save()
