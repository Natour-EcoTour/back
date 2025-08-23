"""
Test cases for terms functionality
"""
# pylint: disable=no-member
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role, Terms


class TermsTests(APITestCase):
    """
    Test the terms views.
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
            username='test_user',
            email='user@gmail.com',
            password='Aa12345678!',
            role=self.user_role
        )

        self.master_user_role, _created = Role.objects.get_or_create(
            id=2,
            defaults={'name': 'master'}
        )

        self.test_master_user = CustomUser.objects.create_user(
            username='master_test_user',
            email='natourmaster@gmail.com',
            password='Aa12345678!',
            role=self.master_user_role
        )
        self.test_master_user.is_staff = True
        self.test_master_user.is_superuser = True
        self.test_master_user.save()

    def test_create_terms(self):
        """
        Ensure term creation is working.
        """
        self.client.force_authenticate(user=self.test_master_user)

        url = reverse('create_terms')
        data = {
            "content": "Terms"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Terms.objects.filter(content="Terms").exists())

    def test_create_policy(self):
        """
        Ensure policy creation is working. 
        """
        self.client.force_authenticate(user=self.test_master_user)

        url = reverse('create_terms')
        data = {
            "content": "Policy"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Terms.objects.filter(content="Policy").exists())

    def test_create_terms_exceed_limit(self):
        """
        Ensure there can only be two contents of the terms model.
        """
        self.client.force_authenticate(user=self.test_master_user)

        Terms.objects.create(content="1")
        Terms.objects.create(content="2")

        url = reverse('create_terms')
        data = {
            "content": "More than 2 terms"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Termos e políticas já criados.",
                      response.data['detail'])

    def test_create_terms_with_empty_content(self):
        """
        Ensure that creating terms with empty content is not allowed.
        """
        self.client.force_authenticate(user=self.test_master_user)

        url = reverse('create_terms')
        data = {
            "content": ""
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.",
                      response.data['content'])

    def test_create_terms_unautorized(self):
        """
        Ensure that only authorized master users can create terms.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('create_terms')
        data = {
            "content": "Create terms while being a normal user"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_terms(self):
        """
        Ensure that terms can be retrieved.
        """
        terms = Terms.objects.create(content="Test terms content")

        url = reverse('get_terms', kwargs={'term_id': terms.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Test terms content")

    def test_get_terms_not_found(self):
        """
        Ensure that a 404 is returned for non-existent terms.
        """
        url = reverse('get_terms', kwargs={'term_id': 999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Termos não encontrados.", response.data['detail'])

    def test_update_terms(self):
        """
        Ensure that terms can be updated.
        """
        self.client.force_authenticate(user=self.test_master_user)

        terms = Terms.objects.create(content="Old content")

        url = reverse('update_terms', kwargs={'term_id': terms.id})
        data = {
            "content": "New content"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "New content")

    def test_update_terms_unauthorized(self):
        """
        Ensure that only authorized master users can update terms.
        """
        self.client.force_authenticate(user=self.test_user)

        terms = Terms.objects.create(content="Old content")

        url = reverse('update_terms', kwargs={'term_id': terms.id})
        data = {
            "content": "New content"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        """
        Clean up after tests.
        """
        Terms.objects.all().delete()
        Role.objects.all().delete()
        return super().tearDown()
