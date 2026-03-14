from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def get_token(client, username, password):
    response = client.post(reverse('token_obtain_pair'), {
        'username': username, 'password': password,
    })
    return response.data.get('access')


class UserListRetrieveTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass1234')

    def test_list_anonymous(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_anonymous(self):
        response = self.client.get(reverse('user-detail', args=[self.user1.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('user-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserCreateTests(APITestCase):

    def test_create_user_anonymous(self):
        response = self.client.post(reverse('user-list'), {
            'username': 'newuser',
            'password': 'securepass123',
            'email': 'new@example.com',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

    def test_create_user_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass1234')
        response = self.client.post(reverse('user-list'), {
            'username': 'existing',
            'password': 'anotherpass',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_created_user_can_login(self):
        self.client.post(reverse('user-list'), {
            'username': 'loginuser',
            'password': 'mypassword123',
        })
        token_resp = self.client.post(reverse('token_obtain_pair'), {
            'username': 'loginuser',
            'password': 'mypassword123',
        })
        self.assertEqual(token_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_resp.data)


class UserUpdateDeleteTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='owner', password='pass1234')
        self.user2 = User.objects.create_user(username='other', password='pass1234')
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')

    def test_update_own_account(self):
        token = get_token(self.client, 'owner', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            reverse('user-detail', args=[self.user1.pk]),
            {'first_name': 'Updated'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_update_other_account_forbidden(self):
        token = get_token(self.client, 'other', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            reverse('user-detail', args=[self.user1.pk]),
            {'first_name': 'Hacked'},
        )
        self.assertIn(response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_update_anonymous_forbidden(self):
        response = self.client.patch(
            reverse('user-detail', args=[self.user1.pk]),
            {'first_name': 'Anon'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_own_account(self):
        token = get_token(self.client, 'owner', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('user-detail', args=[self.user1.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_account_forbidden(self):
        token = get_token(self.client, 'other', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('user-detail', args=[self.user1.pk]))
        self.assertIn(response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_admin_can_delete_any_user(self):
        token = get_token(self.client, 'admin', 'adminpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('user-detail', args=[self.user2.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

