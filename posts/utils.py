import stripe
from django.utils import timezone
from datetime import timedelta

from django.db.models import Count, Case, When, IntegerField, Value, Prefetch

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


def weight_post_tuples_handler(weight_post_tuples, weight, post):
    tuples_indexes = range(len(weight_post_tuples))
    for index in tuples_indexes:
        if post.id == weight_post_tuples[index][1].id:
            updated_tuple = (
                weight_post_tuples[index][0] + weight,
                weight_post_tuples[index][1]
            )
            weight_post_tuples[index] = updated_tuple
            return weight_post_tuples
    weight_post_tuples.append((weight, post))
    return weight_post_tuples


def business_intelligence_algorithm(feed_variables, **kwargs):
    tuples = []
    for key, qs in kwargs.iteritems():
        weight = getattr(feed_variables, key)
        for post in qs:
            weight_post_tuples_handler(tuples, weight, post)
    tuples.sort(reverse=True)
    posts = [y for _, y in tuples]
    return posts


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
