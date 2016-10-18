import stripe
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions, status
from rest_framework.views import APIView

from .serializers import PostSerializer
from .models import Post
from TapVet.settings import STRIPE_API_KEY, PAID_POST_AMOUNT
from helpers.stripe_helpers import stripe_errors_handler


class PostListCreateView(ListCreateAPIView):
    """
    Service to create list and create new vet post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Post.objects.annotate(likes_count=Count('likers'))

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PaidPostView(APIView):
    """Service to set a post as paid

    :accepted method:
        POST
    """
    def __init__(self, **kwargs):
        super(PaidPostView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        post = self.get_object()
        if post.exists():
            post = post.get()
            user = post.user
            if user.stripe_token:
                try:
                    stripe.Charge.create(
                        amount=PAID_POST_AMOUNT,
                        currency='cad',
                        customer=str(user.stripe_token),
                        description='Charge for %s' % user.__str__()
                    )
                except (APIConnectionError, InvalidRequestError, CardError) as err:
                    error = stripe_errors_handler(err)
                    return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    post.set_paid().save()
                    return Response('Payment successful', status=status.HTTP_200_OK)
            no_customer_response = {'detail': 'There is no customer for this user'}
            return Response(no_customer_response, status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def get_object(self):
        """Method to get a Post instance and prefetch the owner of the post

        :return: queryset with Post instance in it
        """
        post = Post.objects.filter(pk=self.kwargs['pk'],
                                   user=self.request.user.id).select_related('user')
        return post
