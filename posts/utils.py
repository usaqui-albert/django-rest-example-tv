import stripe
from django.utils import timezone
from datetime import timedelta

from django.db.models import Count, Case, When, IntegerField, Value, Prefetch
from push_notifications.models import APNSDevice, GCMDevice

from stripe.error import APIConnectionError, InvalidRequestError, CardError
from helpers.stripe_helpers import stripe_errors_handler
from TapVet.settings import STRIPE_API_KEY
from comments.models import Comment


stripe.api_key = STRIPE_API_KEY


def paid_post_handler(user, amount):
    try:
        stripe.Charge.create(
            amount=amount,
            currency='cad',
            customer=str(user.stripe_token),
            description='Charge for %s' % user.__str__()
        )
    except (APIConnectionError, InvalidRequestError, CardError) as err:
        return stripe_errors_handler(err)
    else:
        return True


# helpers to get annotate params
tuple_helper = (
    ('likes_count', Count('likers', distinct=True)),
    ('one_day_recently', Case(
        When(
            created_at__gte=timezone.now() - timedelta(days=1),
            then=Value(1)
        ),
        default=Value(0),
        output_field=IntegerField()
    ))
)


def get_annotate_params(*args):
    return dict([
        (key, value)
        for key, value in tuple_helper
        if key in args
    ])


def handler_images_order(queryset, image_id):
    images = [image for image in queryset if not image.id == image_id]
    images.sort(key=lambda x: x.image_number)
    index_list = range(1, len(images) + 1)
    for image, index in zip(images, index_list):
        image.image_number = index
        image.save()
    return images


# Queries to prefetch
vet_comments_queryset = Comment.objects.select_related(
    'user__groups').filter(user__groups_id__in=[3, 4, 5])
owner_comments_queryset = Comment.objects.select_related(
    'user__groups').filter(user__groups_id__in=[1, 2])

# Prefetch vet and per owner comments
prefetch_vet_comments = Prefetch(
    'comments',
    queryset=vet_comments_queryset,
    to_attr='vet_comments_queryset'
)
prefetch_owner_comments = Prefetch(
    'comments',
    queryset=owner_comments_queryset,
    to_attr='owner_comments_queryset'
)

def get_user_devices(user_id):
    gcm_device = GCMDevice.objects.filter(user=user_id).first()
    apns_device = APNSDevice.objects.filter(user=user_id).first()
    return gcm_device, apns_device
