from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile


User = get_user_model()


class ProfileAPITestCase(APITestCase):
    def test_profile_is_created_for_new_user(self):
        user = User.objects.create_user(
            username='profileuser',
            password='testpass123'
        )

        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.role, 'user')

    def test_admin_profile_role_is_created_for_superuser(self):
        admin_user = User.objects.create_superuser(
            username='adminprofile',
            password='testpass123'
        )

        self.assertTrue(Profile.objects.filter(user=admin_user).exists())
        self.assertEqual(admin_user.profile.role, 'admin')

    def test_authenticated_user_can_view_own_profile(self):
        user = User.objects.create_user(
            username='meuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)

        url = reverse('my-profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')
        self.assertEqual(response.data['role'], 'user')
        self.assertEqual(response.data['id'], user.profile.id)

    def test_superuser_can_view_admin_role_in_own_profile(self):
        admin_user = User.objects.create_superuser(
            username='adminme',
            password='testpass123'
        )
        self.client.force_authenticate(user=admin_user)

        url = reverse('my-profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'adminme')
        self.assertEqual(response.data['role'], 'admin')

    def test_anonymous_user_cannot_view_profile(self):
        url = reverse('my-profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
