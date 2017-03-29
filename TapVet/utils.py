from urllib2 import URLError
from ssl import SSLError

from push_notifications.models import GCMDevice, APNSDevice
from push_notifications import NotificationError


def get_user_devices(user_id):
    gcm_device = GCMDevice.objects.filter(user=user_id).first()
    apns_device = APNSDevice.objects.filter(user=user_id).first()
    return gcm_device, apns_device


def send_notification_message(user_id, message):
    gcm_device, apns_device = get_user_devices(user_id)

    try:
        if gcm_device:
            gcm_device.send_message(message)
        if apns_device:
            apns_device.send_message(message)
    except (NotificationError, URLError, SSLError):
        pass
