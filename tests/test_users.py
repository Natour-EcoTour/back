"""
Test cases for user management functionality
"""
# pylint: disable=no-member
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role, Point


class UsersTests(APITestCase):
    """
    Test the user management views.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.user_role, _created = Role.objects.get_or_create(
            id=1,
            defaults={'name': 'user'}
        )

        self.master_role, _created = Role.objects.get_or_create(
            id=2,
            defaults={'name': 'master'}
        )

        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='Aa12345678!',
            role=self.user_role,
        )

        self.master_user = CustomUser.objects.create_user(
            username='masteruser',
            email='master@example.com',
            password='Aa12345678!',
            role=self.master_role,
            is_staff=True,
            is_superuser=True
        )

        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Aa12345678!',
            role=self.user_role
        )

        self.test_point = Point.objects.create(
            user=self.test_user,
            name='Test Point',
            description='Test description',
            point_type='trail',
            latitude=-22.9068,
            longitude=-43.1729,
            zip_code='22071-900',
            city='Rio de Janeiro',
            neighborhood='Copacabana',
            state='Rio de Janeiro',
            street='Rua Test',
            number='123',
            week_start='2025-01-01',
            week_end='2025-12-31',
            open_time='08:00:00',
            close_time='18:00:00',
            is_active=True,
            status=True
        )

    def test_get_my_info(self):
        """
        Test getting authenticated user's information.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('get_my_info')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'user@example.com')

    def test_get_my_info_unauthenticated(self):
        """
        Test getting user info without authentication should fail.
        """
        url = reverse('get_my_info')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_my_info(self):
        """
        Test updating authenticated user's information.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('update_my_info')
        data = {
            'username': 'updateduser',
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, 'updateduser')

    def test_delete_my_account(self):
        """
        Test deleting authenticated user's account.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('delete_my_account')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(CustomUser.objects.filter(
            id=self.test_user.id).exists())

    def test_get_all_users_as_admin(self):
        """
        Test getting all users as admin with pagination.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('get_all_users')
        response = self.client.get(url, {'page': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIn('total_users', response.data)

    def test_get_all_users_without_page_param(self):
        """
        Test getting all users without page parameter should fail.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('get_all_users')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('paginação', response.data['detail'])

    def test_get_all_users_as_regular_user(self):
        """
        Test getting all users as regular user should fail.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('get_all_users')
        response = self.client.get(url, {'page': 1})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_user_status_as_admin(self):
        """
        Test changing user status as admin.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('change_user_status', kwargs={
                      'user_id': self.other_user.id})
        data = {
            'is_active': False,
            'deactivation_reason': 'Test deactivation'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.other_user.refresh_from_db()
        self.assertFalse(self.other_user.is_active)
        self.assertEqual(self.other_user.deactivation_reason,
                         'Test deactivation')

    def test_change_user_status_as_regular_user(self):
        """
        Test changing user status as regular user should fail.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('change_user_status', kwargs={
                      'user_id': self.other_user.id})
        data = {'is_active': False}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_account_as_admin(self):
        """
        Test deleting user account as admin.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('delete_user_account', kwargs={
                      'user_id': self.other_user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(CustomUser.objects.filter(
            id=self.other_user.id).exists())

    def test_get_user_points_as_admin(self):
        """
        Test getting user's points as admin.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('get_user_points', kwargs={'user_id': self.test_user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_my_points(self):
        """
        Test getting authenticated user's points.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('get_my_points')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('points', response.data)
        self.assertEqual(len(response.data['points']), 1)
        self.assertEqual(response.data['points'][0]['name'], 'Test Point')

    def tearDown(self):
        """
        Clean up after tests.
        """
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        cache.clear()
        return super().tearDown()
