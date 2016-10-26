import stripe

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
