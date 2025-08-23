"""
Test cases for authentication functionality
"""
# pylint: disable=no-member
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role


class AuthTests(APITestCase):
    """
    Test the authentication views.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.user_role, _created = Role.objects.get_or_create(
            id=1,
            defaults={'name': 'user'}
        )

        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            email='vitorantunes2003@gmail.com',
            password='Aa12345678!',
            role=self.user_role
        )

    def test_create_user(self):
        """
        Ensure user creation is working.
        """
        email = 'newuser@example.com'
        cache.set(f'verified_email:{email}', True, timeout=600)

        url = reverse('create_user')
        data = {
            'username': 'newuser',
            'email': email,
            'password': 'Aa12345678!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_login(self):
        """
        Ensure login is working.
        """
        url = reverse('login')
        data = {
            "email": "vitorantunes2003@gmail.com",
            "password": "Aa12345678!",
            "remember_me": True
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']
                         ['email'], "vitorantunes2003@gmail.com")

    def test_get_refresh_token(self):
        """
        Ensure refresh token retrieval is working.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('get_refresh_token')
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_login_with_invalid_credentials(self):
        """
        Test login with invalid credentials.
        """
        url = reverse('login')
        data = {
            "email": "vitorantunes2003@gmail.com",
            "password": "wrong_password"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('error' in response.data)

    def test_create_user_without_email_verification(self):
        """
        Test user creation without email verification should fail.
        """
        url = reverse('create_user')
        data = {
            'username': 'failuser',
            'email': 'fail@example.com',
            'password': 'Aa12345678!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('validar seu e-mail', response.data['detail'])

    def test_login_with_inactive_user(self):
        """
        Test login with inactive user should fail.
        """
        _inactive_user = CustomUser.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='Aa12345678!',
            role=self.user_role,
            is_active=False
        )

        url = reverse('login')
        data = {
            "email": "inactive@example.com",
            "password": "Aa12345678!"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('desativada', response.data['error'])

    def tearDown(self):
        """
        Clean up after tests.
        """
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        cache.clear()
        return super().tearDown()
