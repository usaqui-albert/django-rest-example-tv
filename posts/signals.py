from push_notifications.models import APNSDevice, GCMDevice

from users.tasks import send_report
from activities.models import Activity
from TapVet.messages import liking_post


def post_reporting_signal(sender, instance=None, created=False, **kwargs):
    if created:
        send_report(instance.user, instance)


def new_post_like_signal(sender, instance=None, created=False, **kwargs):
    if created:
        post_owner_id = instance.post.user_id
        gcm_device = GCMDevice.objects.filter(user=post_owner_id).first()
        apns_device = APNSDevice.objects.filter(user=post_owner_id).first()

        if gcm_device:
            gcm_device.send_message(liking_post)
        if apns_device:
            apns_device.send_message(liking_post)

        activity = Activity(
            user=instance.user,
            action=Activity.LIKE,
            post=instance.post
        )
        activity.save()
