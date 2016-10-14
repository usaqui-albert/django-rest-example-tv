"""Testing models"""
import pytest
import tempfile
from PIL import Image

from django.core.management import call_command

from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory, force_authenticate

from .. import views
from .. import models

pytestmark = pytest.mark.django_db


class TestPostVetListCreateView:
    factory = APIRequestFactory()

    def load_data(self):
        call_command(
            'loaddata', '../../users/fixtures/users.json', verbosity=0)

    def test_request_get_no_auth(self):
        req = self.factory.get('/')
        resp = views.PostVetListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_request_get(self):
        self.load_data()
        user = mixer.blend('users.user', groups_id=1)
        req = self.factory.get('/')
        force_authenticate(req, user=user)
        resp = views.PostVetListCreateView.as_view()(req)
        assert resp.status_code == 200, (
            'Should return 200 OK and a list of post'
        )

    def test_request_post_no_auth(self):
        req = self.factory.post('/')
        resp = views.PostVetListCreateView.as_view()(req)
        assert resp.status_code == 401, (
            'Should return Method Unauthorized (401) with a json ' +
            '"detail": "Authentication credentials were not provided."'
        )

    def test_request_post(self):
        self.load_data()
        image = Image.new('RGB', (1000, 1000), 'white')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        user = mixer.blend('users.user', groups_id=1)
        data = {
            'description': 'BLAh blah',
            'image_1': tmp_file
        }
        tmp_file.seek(0)
        req = self.factory.post('/', data=data)
        force_authenticate(req, user=user)
        resp = views.PostVetListCreateView.as_view()(req)
        assert resp.status_code == 201, (
            'Should return HTTP 201 CREATED'
        )
        p = models.Post.objects.last()
        image = p.images.first()
        img_s = Image.open(image.standard)
        img_t = Image.open(image.thumbnail)
        assert img_s.size == (612, 612)
        assert img_t.size == (150, 150)
