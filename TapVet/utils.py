from push_notifications.models import GCMDevice, APNSDevice


def get_user_devices(user_id):
    gcm_device = GCMDevice.objects.filter(user=user_id).first()
    apns_device = APNSDevice.objects.filter(user=user_id).first()
    return gcm_device, apns_device

def send_notification_message(user_id, message):
    gcm_device, apns_device = get_user_devices(user_id)

    if gcm_device:
        gcm_device.send_message(message)
    if apns_device:
        apns_device.send_message(message)
