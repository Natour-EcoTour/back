"""
Test cases for photo management functionality
"""
# pylint: disable=no-member
import io
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from natour.api.models import CustomUser, Role, Photo, Point


class PhotoTests(APITestCase):
    """
    Test the photo management views.
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
            close_time='18:00:00'
        )

    def create_test_image(self):
        """
        Create a test image file for upload tests.
        """
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'

        return SimpleUploadedFile(
            name='test_image.png',
            content=image_content,
            content_type='image/png'
        )

    def test_create_user_photo(self):
        """
        Test uploading photo for user.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('user-photo-upload',
                      kwargs={'user_id': self.test_user.id})
        image_file = self.create_test_image()

        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Photo.objects.filter(user=self.test_user).exists())

    def test_create_point_photo(self):
        """
        Test uploading photo for point.
        """
        self.client.force_authenticate(user=self.test_user)

        url = reverse('point-photo-upload',
                      kwargs={'point_id': self.test_point.id})
        image_file = self.create_test_image()

        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Photo.objects.filter(point=self.test_point).exists())

    def test_create_photo_unauthenticated(self):
        """
        Test uploading photo without authentication.
        """
        url = reverse('user-photo-upload',
                      kwargs={'user_id': self.test_user.id})
        image_file = self.create_test_image()

        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_photos_by_user(self):
        """
        Test getting photos by user ID.
        """
        url = reverse('photo-list')
        response = self.client.get(url, {'user_id': self.test_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_photos_by_point(self):
        """
        Test getting photos by point ID.
        """
        url = reverse('photo-list')
        response = self.client.get(url, {'point_id': self.test_point.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_photos_without_params(self):
        """
        Test getting photos without user_id or point_id should fail.
        """
        url = reverse('photo-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_id', response.data['detail'])

    def test_update_user_photo(self):
        """
        Test updating user photo.
        """
        photo = Photo.objects.create(
            user=self.test_user,
            image='http://example.com/test.jpg',
            public_id='test_public_id'
        )

        self.client.force_authenticate(user=self.test_user)

        url = reverse('user-photo-update', kwargs={
            'user_id': self.test_user.id,
            'photo_id': photo.id
        })
        image_file = self.create_test_image()

        data = {'image': image_file}
        response = self.client.put(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        """
        Clean up after tests.
        """
        Photo.objects.all().delete()
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        Point.objects.all().delete()
        return super().tearDown()
