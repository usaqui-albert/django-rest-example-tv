from operator import xor

from django.http import Http404
from django.db import IntegrityError
from django.db.models import (
    Case, When, Value, IntegerField, F, BooleanField, Q
)
from django.utils import timezone
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateAPIView, ListAPIView, DestroyAPIView,
    get_object_or_404, GenericAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework import permissions, status
from rest_framework.views import APIView

from TapVet import messages
from TapVet.permissions import IsVet
from TapVet.pagination import StandardPagination, CardsPagination
from TapVet.permissions import IsOwnerOrReadOnly
from .serializers import (
    PostSerializer, PaymentAmountSerializer, ImagePostSerializer,
    PaidPostSerializer, ReportTypeSerializer
)
from activities.models import Activity

from .models import Post, PaymentAmount, ImagePost, UserLikesPost, Report
from .utils import (
    get_annotate_params, handler_images_order,
    prefetch_vet_comments, prefetch_owner_comments
)


class PostListCreateView(ListCreateAPIView):
    """
    Service to create list and create new post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = StandardPagination

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            serializer = self.serializer_class(
                data=request.data,
                context={
                    'user': request.user,
                    'request': request
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(
            {'detail': messages.user_login},
            status=status.HTTP_401_UNAUTHORIZED
        )

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except ValidationError as err:
            return Response(
                {'detail': err.message},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        user = self.request.user
        annotate_params = get_annotate_params(
            'one_day_recently',
            'likes_count'
        )
        if user.is_authenticated():
            annotate_params['case_1'] = Case(
                When(
                    pk__in=user.likes.all(),
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
            annotate_params['case_2'] = Case(
                When(
                    pk__in=self.get_posts_ids(),
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
            annotate_params['case_3'] = Case(
                When(
                    user__in=user.follows.all(),
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
            annotate_params['case_4'] = Case(
                When(
                    user=user.id,
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
            annotate_params['points'] = F('case_1') + F('case_2') + \
                F('case_3') + F('case_4') + F('one_day_recently')
            annotate_params['interested'] = F('case_1')
            group_id = user.groups.id
            if group_id in [3, 4, 5]:
                filters = Q(visible_by_vet=True, visible_by_owner=False)
            else:
                filters = Q(visible_by_owner=True)
        else:
            veterinarian = bool(self.request.query_params.get('vet', None))
            pet_owner = bool(self.request.query_params.get('owner', None))
            if xor(veterinarian, pet_owner):
                if veterinarian:
                    filters = Q(visible_by_vet=True, visible_by_owner=False)
                else:
                    filters = Q(visible_by_owner=True)
            else:
                raise ValidationError('Invalid query params')
        return self.helper(annotate_params, filters, user.is_authenticated())

    @staticmethod
    def helper(annotate_params, filters, is_authenticated):
        posts = Post.objects.annotate(
            **annotate_params
        ).select_related(
            'user__groups',
            'user__image'
        ).prefetch_related(
            'images',
            prefetch_vet_comments,
            prefetch_owner_comments
        ).filter(filters).exclude(active=False)
        if is_authenticated:
            posts = posts.order_by('-points', '-id')
        else:
            posts = posts.order_by('-id')
        return posts

    def get_posts_ids(self):
        posts_ids = []
        comments = self.request.user.comments.all()
        for comment in comments:
            post_id = comment.post_id
            if post_id not in posts_ids:
                posts_ids.append(post_id)
        return posts_ids or [0]


class PostRetrieveUpdateView(RetrieveUpdateDestroyAPIView):
    """
    Service to delete  posts.

    :accepted methods:
    GET
    PUT
    PATCH
    DELETE
    """
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        annotate_params = get_annotate_params('likes_count')
        if self.request.user.is_authenticated():
            annotate_params['interested'] = Case(
                When(
                    pk__in=self.request.user.likes.all(),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        queryset = Post.objects.annotate(
            **annotate_params
        ).prefetch_related(
            prefetch_vet_comments,
            prefetch_owner_comments
        ).exclude(active=False)
        return queryset.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.save()
        Activity.objects.filter(post=instance).update(active=False)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageView(GenericAPIView):
    serializer_class = ImagePostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        post = self.get_post()
        if request.user.id == post.user_id:
            image_number = post.images.count() + 1
            if image_number > 3:
                return Response(
                    messages.too_much_images,
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            new_image = request.data.get('image', None)
            if new_image:
                # Faking a post serializer instance to use create_image_post
                # method, shouldn't be like this by the way.
                serializer = PostSerializer(post, data={}, partial=True)
                image_post = serializer.create_image_post(
                    new_image,
                    post,
                    image_number
                )
                post.save()
                image_serializer = self.serializer_class(
                    image_post,
                    context={'request': request}
                )
                return Response(
                    image_serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                messages.image_required,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            messages.forbidden_action,
            status=status.HTTP_403_FORBIDDEN
        )

    def get_post(self):
        post = Post.objects.filter(
            pk=self.kwargs.get('pk', None)
        ).select_related(
            'user'
        ).first()
        if post:
            return post
        raise Http404()


class ImageDetailView(DestroyAPIView):
    serializer_class = ImagePostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, **kwargs):
        image = self.get_queryset()
        post = image.post
        if post.user == request.user or request.user.is_staff:
            new_image = request.data.get('image', None)
            if new_image:
                # Faking a post serializer instance to use update_image_post
                # method, shouldn't be like this by the way.
                serializer = PostSerializer(post, data={}, partial=True)
                image_post = serializer.update_image_post(new_image, image)
                post.save()
                image_serializer = self.serializer_class(
                    image_post,
                    context={'request': request}
                )
                return Response(
                    image_serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                messages.image_required,
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            response = {
                'detail': messages.permission
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, *args, **kwargs):
        image = self.get_queryset()
        post = image.post
        images = post.images.all()
        if post.user == request.user or request.user.is_staff:
            if images.count() > 1:
                handler_images_order(images, int(image.id))
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

    def get_queryset(self):
        queryset = ImagePost.objects.select_related(
            'post__user'
        ).prefetch_related(
            'post__images'
        ).filter(
            pk=self.kwargs['pk_image'],
            post=self.kwargs['pk_post']
        ).first()
        if queryset:
            return queryset
        raise Http404()


class PaidPostView(APIView):
    """Service to set a post as paid

    :accepted method:
        POST
    """

    allowed_methods = ('POST',)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        post = self.get_object().first()
        if post:
            if post.user.is_vet():
                return Response(
                    {'detail': "Vet community does not have paid post"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            post.set_paid().save()
            return Response(
                {'detail': 'Payment successful'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_object(self):
        """
        Method to get a Post instance and prefetch the owner of the post
        and group

        :return: queryset with Post instance in it
        """
        post = Post.objects.filter(
            pk=self.kwargs['pk'],
            user=self.request.user.id
        ).select_related('user__groups')
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
    permission_classes = (permissions.AllowAny,)
    serializer_class = PostSerializer

    def get_queryset(self):
        qs = Post.objects.annotate(
            **get_annotate_params('likes_count')
        ).filter(user_id=self.kwargs['pk']).prefetch_related(
            'images',
            prefetch_vet_comments,
            prefetch_owner_comments
        ).exclude(active=False).exclude(active=False).order_by('-id')
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
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get_post(pk):
        return Post.objects.filter(pk=pk).first()

    def post(self, request, **kwargs):
        post = self.get_post(pk=kwargs['pk'])
        if post:
            try:
                UserLikesPost.objects.create(
                    user=request.user,
                    post=post
                )
            except IntegrityError:
                return Response(
                    messages.already_liked,
                    status=status.HTTP_409_CONFLICT
                )
            else:
                post.updated_at = timezone.now()
                return Response(status=status.HTTP_201_CREATED)
        return Response(
            messages.post_not_found,
            status=status.HTTP_404_NOT_FOUND
        )

    def delete(self, request, **kwargs):
        post = self.get_post(pk=kwargs['pk'])
        if post:
            obj = get_object_or_404(
                UserLikesPost,
                user=request.user.id,
                post=post.id
            )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            messages.post_not_found,
            status=status.HTTP_404_NOT_FOUND
        )


class PostPaidListView(ListAPIView):
    """
    Service to obtain only paid post. This will allow to make vets cards easy.
    :Auth Required:
    :Vet Required:
    :accepted methods:
    GET
    """
    pagination_class = CardsPagination
    permission_classes = (IsVet,)
    serializer_class = PaidPostSerializer

    def get_queryset(self):
        id_list = Post.objects.filter(
            visible_by_vet=True, visible_by_owner=True
        ).exclude(
            comments__user_id=self.request.user.id
        ).prefetch_related(
            prefetch_vet_comments
        ).order_by(
            '-updated_at', '-comments'
        ).values_list('id', flat=True)
        id_set = self.f7(id_list)
        preserved = Case(
            *[
                When(
                    pk=pk,
                    then=pos
                ) for pos, pk in enumerate(id_set)
            ]
        )
        new = Post.objects.filter(id__in=id_set).order_by(preserved)
        return new

    @staticmethod
    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]


class PostReportView(GenericAPIView):
    """
    Service for a user reports a post

    :accepted methods:
        POST
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ReportTypeSerializer

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = get_object_or_404(Post, pk=kwargs['pk'])
        try:
            Report.objects.create(
                user=request.user,
                post=post,
                type=serializer.validated_data['type']
            )
        except IntegrityError:
            return Response(
                messages.post_already_reported,
                status=status.HTTP_409_CONFLICT
            )
        else:
            return Response(status=status.HTTP_201_CREATED)
