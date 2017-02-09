from TapVet.utils import send_notification_message
from activities.models import Activity
from TapVet.messages import (
    commenting_post, upvoting_comment, vet_commenting_post
)


def new_comment_signal(sender, instance=None, created=False, **kwargs):
    if created:
        post = instance.post
        user = instance.user
        post_owner = post.user

        if (post.is_paid() and user.is_vet() and
                post_owner.vet_reply_notification):
            send_notification_message(post_owner.id, vet_commenting_post)
        elif post_owner.comments_notification:
            send_notification_message(post_owner.id, commenting_post)

        activity = Activity(
            user=user,
            action=Activity.COMMENT,
            post=post,
            comment=instance
        )
        activity.save()


def upvoters_changed(sender, action=None, pk_set=None, **kwargs):
    if action == 'post_add' and pk_set:
        instance = kwargs['instance']
        if instance.user.comments_like_notification:
            send_notification_message(instance.user.id, upvoting_comment)

        activity = Activity(
            user_id=pk_set.pop(),
            action=Activity.UPVOTE,
            comment=instance,
            post=instance.post
        )
        activity.save()
