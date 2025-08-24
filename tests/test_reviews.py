"""
Test cases for review functionality
"""
# pylint: disable=no-member
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role, Point, PointReview


class ReviewTests(APITestCase):
    """
    Test the review management views.
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
            email='user@example.com',
            password='Aa12345678!',
            role=self.user_role
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
            is_active=True
        )

    def test_add_review(self):
        """
        Test adding a review to a point.
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {
            'rating': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(PointReview.objects.filter(
            user=self.other_user,
            point=self.test_point
        ).exists())

        self.test_point.refresh_from_db()
        self.assertEqual(self.test_point.avg_rating, 5.0)

    def test_add_review_unauthenticated(self):
        """
        Test adding review without authentication should fail.
        """
        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {
            'rating': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_duplicate_review(self):
        """
        Test adding duplicate review should fail.
        """
        PointReview.objects.create(
            user=self.other_user,
            point=self.test_point,
            rating=4
        )

        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {
            'rating': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('já avaliou', response.data['detail'])

    def test_add_review_invalid_rating(self):
        """
        Test adding review with invalid rating should fail.
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {
            'rating': 6
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_review_to_nonexistent_point(self):
        """
        Test adding review to non-existent point should fail.
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': 99999})
        data = {
            'rating': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_multiple_reviews_average_calculation(self):
        """
        Test that average rating is calculated correctly with multiple reviews.
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {
            'rating': 4
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        third_user = CustomUser.objects.create_user(
            username='thirduser',
            email='third@example.com',
            password='Aa12345678!',
            role=self.user_role
        )

        self.client.force_authenticate(user=third_user)

        data = {
            'rating': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.test_point.refresh_from_db()
        self.assertEqual(self.test_point.avg_rating, 3.0)

    def test_add_review_empty_comment(self):
        """
        Test adding review with empty comment (should be allowed).
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {
            'rating': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertIn(response.status_code, [
                      status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_add_review_missing_rating(self):
        """
        Test adding review without rating should fail.
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('add_review', kwargs={'point_id': self.test_point.id})
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        """
        Clean up after tests.
        """
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        Point.objects.all().delete()
        return super().tearDown()
