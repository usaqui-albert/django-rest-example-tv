from activities.models import Activity


def new_comment_signal(sender, instance=None, created=False, **kwargs):
    if created:
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
