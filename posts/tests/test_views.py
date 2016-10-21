"""Testing views"""
import pytest
import tempfile

from PIL import Image
from rest_framework.test import force_authenticate
from mixer.backend.django import mixer

from .. import views
from .. import models
from helpers.tests_helpers import CustomTestCase

pytestmark = pytest.mark.django_db


class TestPostVetListCreateView(CustomTestCase):

    def test_request_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.PostListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_request_get(self):
        user = self.load_users_data().get_user(groups_id=1)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PostListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return 200 OK and a list of post'
        )

    def test_request_get_many_likes(self):
        self.load_users_data()
        users = [mixer.blend('users.user', groups_id=1) for _ in range(30)]
        user = mixer.blend('users.user', groups_id=1)
        [mixer.blend(
            'posts.post', user=user, likers=[x for x in users])
            for _ in range(10)]
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PostListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return 200 OK and a list of post'
        )
        assert [post['likes_count'] == 30 for post in resp.data]

    def test_request_post_no_auth(self):
        req = self.factory.post('/')
        resp = views.PostListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_request_post(self):
        image = Image.new('RGB', (1000, 1000), 'white')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        user = self.load_users_data().get_user(groups_id=1)
        data = {
            'description': 'BLAh blah',
            'image_1': tmp_file
        }
        tmp_file.seek(0)
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PostListCreateView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return HTTP 201 CREATED'
        )
        p = models.Post.objects.last()
        image = p.images.first()
        img_s = Image.open(image.standard)
        img_t = Image.open(image.thumbnail)
        assert img_s.size == (612, 612)
        assert img_t.size == (150, 150)


class TestPaidPostView(CustomTestCase):

    def test_user_no_authenticated(self):
        req = self.factory.post('/')
        resp = views.PaidPostView.as_view()(req)
        assert resp.status_code == 401, 'Should return Unauthorized (401)'

    def test_get_request_not_allowed(self):
        user = self.get_user()
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PaidPostView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_put_request_not_allowed(self):
        user = self.get_user()
        req = self.factory.put('/')
        force_authenticate(req, user=user)
        resp = views.PaidPostView.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_post_does_not_exists(self):
        req = self.factory.post('/')
        force_authenticate(req, user=self.get_user())
        resp = views.PaidPostView.as_view()(req, pk=1)
        assert resp.status_code == 404, (
            'Should return Not Found (404) post with pk=1 does not exist')

    def test_user_isnt_post_owner(self):
        user_owner = self.load_users_data().get_user(groups_id=1)
        mixer.blend('posts.Post', user=user_owner, pk=1)

        user_requesting = self.get_user()
        req = self.factory.post('/')
        force_authenticate(req, user=user_requesting)

        resp = views.PaidPostView.as_view()(req, pk=1)
        assert resp.status_code == 404, (
            'Should return Not Found (404) post with pk=1 exists but the'
            'user requesting is not the owner'
        )

    def test_user_has_no_stripe_customer(self):
        user = self.load_users_data().get_user(groups_id=1,
                                               stripe_token=None)
        mixer.blend('posts.Post', user=user, pk=1)

        req = self.factory.post('/')
        force_authenticate(req, user=user)

        resp = views.PaidPostView.as_view()(req, pk=1)
        assert resp.status_code == 402, (
            'Should return Payment Required (402) user has no a related '
            'stripe customer'
        )


class TestPaymentAmountDetail(CustomTestCase):

    def test_post_request_not_allowed(self):
        req = self.factory.post('/')
        force_authenticate(req, user=self.get_user())

        resp = views.PaymentAmountDetail.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_delete_request_not_allowed(self):
        req = self.factory.delete('/')
        force_authenticate(req, user=self.get_user())

        resp = views.PaymentAmountDetail.as_view()(req)
        assert resp.status_code == 405, (
            'Should return Method Not Allowed (405)')

    def test_get_request_no_authenticated_user(self):
        req = self.factory.get('/')

        resp = views.PaymentAmountDetail.as_view()(req)
        assert resp.status_code == 401, 'Should return Unauthorized (401)'

    def test_get_request_any_authenticated_user(self):
        payment_amount = mixer.blend('posts.PaymentAmount')
        req = self.factory.get('/')
        force_authenticate(req, user=self.get_user())

        resp = views.PaymentAmountDetail.as_view()(req, pk=payment_amount.pk)
        assert resp.status_code == 200, 'Should return OK (200)'

    def test_put_request_no_authenticated_user(self):
        req = self.factory.put('/')

        resp = views.PaymentAmountDetail.as_view()(req)
        assert resp.status_code == 401, 'Should return Unauthorized (401)'

    def test_put_request_any_authenticated_user(self):
        req = self.factory.put('/')
        force_authenticate(req, user=self.get_user())

        resp = views.PaymentAmountDetail.as_view()(req)
        assert 'detail' in resp.data
        assert resp.data['detail'] == 'You are not an admin user'
        assert resp.status_code == 403, 'Should return Forbidden (403)'

    def test_put_request_with_no_data_admin_user(self):
        payment_amount = mixer.blend('posts.PaymentAmount')
        req = self.factory.put('/', {})
        force_authenticate(req, user=self.get_user(is_staff=True))

        resp = views.PaymentAmountDetail.as_view()(req, pk=payment_amount.pk)
        assert 'description' in resp.data, (
            'Given description is a required field the updating data should '
            'contain a description field'
        )
        assert 'This field is required.' in resp.data['description']
        assert resp.status_code == 400, (
            'Should return Bad Request (400)')

    def test_put_request_with_empty_data_admin_user(self):
        payment_amount = mixer.blend('posts.PaymentAmount')
        req = self.factory.put('/', {'description': ''})
        force_authenticate(req, user=self.get_user(is_staff=True))

        resp = views.PaymentAmountDetail.as_view()(req, pk=payment_amount.pk)
        assert 'description' in resp.data
        assert 'This field may not be blank.' in resp.data['description']
        assert resp.status_code == 400, (
            'Shour return Bad Request (400)')
