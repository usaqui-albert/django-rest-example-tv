import stripe

from django.db.models import Count, Case, When, IntegerField

from stripe.error import APIConnectionError, InvalidRequestError, CardError
from helpers.stripe_helpers import stripe_errors_handler
from TapVet.settings import STRIPE_API_KEY

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
    ('vet_comments',
     Count(
         Case(
             When(
                 comments__user__groups_id__in=[3, 4, 5],
                 then=1
             ),
             output_field=IntegerField()
         )
     )),
    ('owner_comments',
     Count(
         Case(
             When(
                 comments__user__groups_id__in=[1, 2],
                 then=1
             ),
             output_field=IntegerField()
         )
     )),
    ('likes_count', Count('likers', distinct=True)),
)


def get_annotate_params(*args):
    return dict([
        (key, value)
        for key, value in tuple_helper
        if key in args
    ])
