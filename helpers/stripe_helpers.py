import stripe

from stripe.error import APIConnectionError, InvalidRequestError, CardError


def stripe_errors_handler(error):
    """Method to search the exactly string of the error message

    :param error: error response directly from stripe
    :return: stripe error message (string)
    """
    response = ''
    if isinstance(error, APIConnectionError):
        response = str(error).split('.')[0]
    if isinstance(error, InvalidRequestError) or isinstance(error, CardError):
        body = error.json_body
        response = str(body['error']['message'])
    return response


def get_customer_in_stripe(instance):
    """Method to get the stripe customer related with a TapVet user

    :param instance: User instance
    :return: stripe customer or a stripe error message (string)
    """
    if instance.stripe_token:
        try:
            customer = stripe.Customer.retrieve(instance.stripe_token)
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            error = stripe_errors_handler(err)
        else:
            return customer
    else:
        error = "There is no stripe customer available for this user"
    return error


def card_list(queryset):
    return [{"id": i.id,
             "brand": i.brand,
             "last4": i.last4,
             "expiration_month": i.exp_month,
             "expiration_year": i.exp_year} for i in queryset]
