import stripe

from django.conf import settings
from django.db.models import Count, Case, When, IntegerField
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateAPIView, ListAPIView, DestroyAPIView,
    RetrieveUpdateDestroyAPIView)
from rest_framework import permissions, status
from rest_framework.views import APIView

from TapVet import messages
from TapVet.pagination import StandardPagination
from pets.permissions import IsOwnerReadOnly
from .serializers import (
    PostSerializer, PaymentAmountSerializer, ImagePostSerializer
)
from .models import Post, PaymentAmount, ImagePost
from .utils import paid_post_handler


class PostListCreateView(ListCreateAPIView):
    """
    Service to create list and create new post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardPagination
    queryset = Post.objects.annotate(
        vet_comments=Count(
            Case(
                When(
                    comments__post__user__groups_id__in=[3, 4, 5],
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        owner_comments=Count(
            Case(
                When(
                    comments__post__user__groups_id__in=[1, 2],
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        likes_count=Count('likers')
    )

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PostRetriveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    Service to delete  posts.

    :accepted methods:
    GET
    PUT
    PATCH
    DELETE
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerReadOnly)
    queryset = Post.objects.annotate(
        vet_comments=Count(
            Case(
                When(
                    comments__post__user__groups_id__in=[3, 4, 5],
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        owner_comments=Count(
            Case(
                When(
                    comments__post__user__groups_id__in=[1, 2],
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        likes_count=Count('likers')
    )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        images = instance.images.all()
        map(lambda x: x.delete(), images)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImagePostDeleteView(DestroyAPIView):
    serializer_class = ImagePostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ImagePost.objects.all()

    def delete(self, request, *args, **kwargs):
        image = get_object_or_404(ImagePost, pk=kwargs['pk'])
        post = image.post
        images = post.images.count()
        if post.user == request.user or request.user.is_staff:
            if images >= 2:
                image.delete()
                post.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                response = {
                    'detail': messages.one_image
                }
                return Response(
                    response, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            response = {
                'detail': messages.permission
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class PaidPostView(APIView):
    """Service to set a post as paid

    :accepted method:
        POST
    """
    def __init__(self, **kwargs):
        super(PaidPostView, self).__init__(**kwargs)
        stripe.api_key = settings.STRIPE_API_KEY

    allowed_methods = ('POST',)
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
                response = paid_post_handler(user, settings.PAID_POST_AMOUNT)
                if response is True:
                    post.set_paid().save()
                    return Response({'detail': 'Payment successful'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'detail': response},
                                    status=status.HTTP_400_BAD_REQUEST)
            no_customer_response = {
                'detail': 'There is no customer for this user'}
            return Response(
                no_customer_response, status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(
            {'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def get_object(self):
        """Method to get a Post instance and prefetch the owner of the post

        :return: queryset with Post instance in it
        """
        post = Post.objects.filter(
            pk=self.kwargs['pk'],
            user=self.request.user.id).select_related('user')
        return post


class PaymentAmountDetail(RetrieveUpdateAPIView):
    """Service to retrieve and update the price and description of a payment amount

    :accepted methods:
        GET
        PUT
    """
    queryset = PaymentAmount.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentAmountSerializer

    def update(self, request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        if request.user.is_staff:
            return super(PaymentAmountDetail, self).update(request, **kwargs)
        response = {'detail': 'You are not an admin user'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)


class PostByUserListView(ListAPIView):
    """Service to list a post by user

    :accepted methods:
        GET
    """
    pagination_class = StandardPagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PostSerializer
    queryset = Post.objects.annotate(
        vet_comments=Count(
            Case(
                When(
                    comments__post__user__groups_id__in=[3, 4, 5],
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        owner_comments=Count(
            Case(
                When(
                    comments__post__user__groups_id__in=[1, 2],
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        likes_count=Count('likers')
    )

    def get_queryset(self):
        qs = self.queryset
        qs = qs.filter(user_id=self.kwargs['pk'])
        return qs


class PostVoteView(APIView):
    """
    Service to upvote and downvote a comment.
    :Auth Required:
    :accepted methods:
    POST
    DELETE
    """
    allowed_methods = ('POST', 'DELETE')
    permission_classes = (permissions.IsAuthenticated, )

    def get_post(self, pk):
        qs = Post.objects.filter(pk=pk)
        qs.update(updated_at=timezone.now())
        return qs.first()

    def post(self, request, *args, **kwargs):
        post = self.get_post(pk=kwargs['pk'])
        post.likers.add(request.user.id)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        post = self.get_post(pk=kwargs['pk'])
        post.likers.remove(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
