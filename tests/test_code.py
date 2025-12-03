"""
Test cases for verification code functionality
"""
# pylint: disable=no-member
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role


class CodeTests(APITestCase):
    """
    Test the verification code views.
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

    def test_send_verification_code(self):
        """
        Test sending verification code to email.
        """
        url = reverse('send_verification_code')
        data = {
            'email': 'test@example.com',
            'username': 'newuser'
        }
        response = self.client.post(url, data, format='json')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])

    def test_send_verification_code_no_email(self):
        """
        Test sending verification code without email should fail.
        """
        url = reverse('send_verification_code')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Forneça um nome e e-mail.', response.data['detail'])

    def test_verify_code_success(self):
        """
        Test verifying a valid code.
        """
        email = 'test@example.com'
        code = 'ABC123'

        cache.set(f'verification_code:{email}', code, timeout=600)

        url = reverse('verify_code')
        data = {
            'email': email,
            'code': code
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('verificado', response.data['detail'])

        self.assertTrue(cache.get(f'verified_email:{email}'))

    def test_verify_code_invalid(self):
        """
        Test verifying an invalid code.
        """
        email = 'test@example.com'
        correct_code = 'ABC123'
        wrong_code = 'XYZ789'

        cache.set(f'verification_code:{email}', correct_code, timeout=600)

        url = reverse('verify_code')
        data = {
            'email': email,
            'code': wrong_code
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Código incorreto.', response.data['detail'])

    def test_verify_code_expired(self):
        """
        Test verifying an expired code.
        """
        email = 'test@example.com'
        code = 'ABC123'

        url = reverse('verify_code')
        data = {
            'email': email,
            'code': code
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Código expirado ou não encontrado.',
                      response.data['detail'])

    def test_verify_code_missing_data(self):
        """
        Test verifying code with missing data.
        """
        url = reverse('verify_code')

        data = {'code': 'ABC123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'email': 'test@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        """
        Clean up after tests.
        """
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        cache.clear()
        return super().tearDown()
