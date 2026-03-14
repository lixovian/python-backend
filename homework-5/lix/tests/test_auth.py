from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class JWTAuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='auth_user', password='testpass123')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_obtain_token_valid_credentials(self):
        response = self.client.post(self.token_url, {
            'username': 'auth_user',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        response = self.client.post(self.token_url, {
            'username': 'auth_user',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_missing_fields(self):
        response = self.client.post(self.token_url, {'username': 'auth_user'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_nonexistent_user(self):
        response = self.client.post(self.token_url, {
            'username': 'nobody',
            'password': 'whatever',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        obtain = self.client.post(self.token_url, {
            'username': 'auth_user',
            'password': 'testpass123',
        })
        refresh_token = obtain.data['refresh']
        response = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(self.refresh_url, {'refresh': 'invalid.token.here'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _get_token(self):
        response = self.client.post(self.token_url, {
            'username': 'auth_user',
            'password': 'testpass123',
        })
        return response.data['access']

    def test_protected_endpoint_without_token(self):
        url = reverse('post-list')
        response = self.client.post(url, {'title': 'T', 'content': 'C'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        token = self._get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('post-list')
        response = self.client.post(url, {'title': 'Test Post', 'content': 'Content'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

