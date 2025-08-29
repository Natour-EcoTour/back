"""
Test cases for point management functionality
"""
# pylint: disable=no-member
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role, Point


class PointTests(APITestCase):
    """
    Test the point management views.
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
            role=self.user_role
        )

        self.master_user = CustomUser.objects.create_user(
            username='masteruser',
            email='master@example.com',
            password='Aa12345678!',
            role=self.master_role,
            is_staff=True,
            is_superuser=True
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
            week_start='monday',
            week_end='sunday',
            open_time='08:00:00',
            close_time='18:00:00',
            is_active=True,
            status=True
        )

    def test_create_point(self):
        """
        Test creating a new point.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('create_point')
        data = {
            'name': 'New Test Point',
            'description': 'A beautiful new location',
            'point_type': 'water_fall',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'zip_code': '01310-100',
            'city': 'São Paulo',
            'neighborhood': 'Bela Vista',
            'state': 'São Paulo',
            'street': 'Avenida Paulista',
            'number': '1000',
            'week_start': 'monday',
            'week_end': 'sunday',
            'open_time': '07:00:00',
            'close_time': '19:00:00',
            'link': 'https://example.com'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Point.objects.filter(name='New Test Point').exists())

        created_point = Point.objects.get(name='New Test Point')
        self.assertFalse(created_point.is_active)

    def test_create_point_unauthenticated(self):
        """
        Test creating point without authentication should fail.
        """
        url = reverse('create_point')
        data = {'name': 'Test Point'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_point_info(self):
        """
        Test getting point information.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('get_point_info', kwargs={
                      'point_id': self.test_point.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Point')
        self.assertEqual(response.data['description'], 'Test description')

    def test_get_all_points_as_admin(self):
        """
        Test getting all points as admin.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('get_all_points')
        response = self.client.get(url, {'page': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_point_approval_as_admin(self):
        """
        Test approving a point as admin.
        """
        self.client.force_authenticate(user=self.master_user)

        self.test_point.status = False
        self.test_point.is_active = False
        self.test_point.save()

        url = reverse('point_approval', kwargs={
                      'point_id': self.test_point.id})
        data = {
            'status': True,
            'is_active': True
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_point.refresh_from_db()
        self.assertTrue(self.test_point.status)
        self.assertTrue(self.test_point.is_active)

    def test_point_approval_as_regular_user(self):
        """
        Test point approval as regular user should fail.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('point_approval', kwargs={
                      'point_id': self.test_point.id})
        data = {'status': True}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_point_as_owner(self):
        """
        Test editing point as the owner.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('edit_point', kwargs={'point_id': self.test_point.id})
        data = {
            'name': 'Updated Point Name',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_point.refresh_from_db()
        self.assertEqual(self.test_point.name, 'Updated Point Name')

    def test_edit_point_as_non_owner(self):
        """
        Test editing point as non-owner should fail.
        """
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Aa12345678!',
            role=self.user_role
        )

        self.client.force_authenticate(user=other_user)

        url = reverse('edit_point', kwargs={'point_id': self.test_point.id})
        data = {'name': 'Hacked Name'}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_my_point(self):
        """
        Test deleting own point.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('delete_my_point', kwargs={
                      'point_id': self.test_point.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Point.objects.filter(id=self.test_point.id).exists())

    def test_delete_point_as_admin(self):
        """
        Test deleting point as admin.
        """
        self.client.force_authenticate(user=self.master_user)

        url = reverse('delete_point', kwargs={'point_id': self.test_point.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Point.objects.filter(id=self.test_point.id).exists())

    def test_add_view(self):
        """
        Test incrementing point view count.
        """
        self.client.force_authenticate(user=self.test_user)

        initial_views = self.test_point.views

        url = reverse('add_view', kwargs={'point_id': self.test_point.id})
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_point.refresh_from_db()
        self.assertEqual(self.test_point.views, initial_views + 1)

    def test_show_points_on_map(self):
        """
        Test getting points for map display.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('show_points_on_map')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)

    def test_change_point_status(self):
        """
        Test changing point status (user deactivating their own point).
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('change_point_status', kwargs={
                      'point_id': self.test_point.id})
        data = {
            'is_active': False,
            'deactivation_reason': 'Temporarily closed'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_point.refresh_from_db()
        self.assertFalse(self.test_point.is_active)

    def tearDown(self):
        """
        Clean up after tests.
        """
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        Point.objects.all().delete()
        return super().tearDown()
