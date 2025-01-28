from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Item, Profile


class RegistrationTest(APITestCase):
    def test_create_registration(self):
        response = self.client.post(
            reverse('backend:sign-up'),
            {
                "name": "jo",
                "username": "jo22",
                "password": "222",
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Profile.objects.filter(username="jo22").exists()
        )


class LoginTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        cls.profile = Profile.objects.create_user(last_name="jo", username="jo22", password="222")

    @classmethod
    def tearDownClass(cls):
        cls.profile.delete()

    def setUp(self):
        self.client.force_login(self.profile)

    def test_login(self):
        response = self.client.post(
            reverse('backend:sign-in'),
            {
                "username": "jo22",
                "password": "222",
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Item.objects.create(title="Best Product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product_id(self):
        response = self.client.get(reverse('backend:product_id', kwargs={"id": self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_and_check_links(self):
        response = self.client.get(
            reverse(
                'backend:product_id',
                kwargs={"id": self.product.pk},
            ),
        )
        self.assertContains(response, self.product.title)


class ReviewTest(APITestCase):
    def test_create_review(self):
        response = self.client.post(
            reverse('backend:product_id_review', kwargs={"id": 2}),
            {
                "author": "admin",
                "email": "admin@example.ru",
                "text": "rwrwrwrwrw",
                "rate": 4,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

