from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lix.models import Post, PostLike


def get_token(client, username, password):
    response = client.post(reverse('token_obtain_pair'), {
        'username': username, 'password': password,
    })
    return response.data.get('access')


class PostListRetrieveTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='author', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Hello', content='World'
        )

    def test_list_anonymous(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_anonymous(self):
        response = self.client.get(reverse('post-detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Hello')

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('post-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostCreateTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass1234')

    def test_create_anonymous_forbidden(self):
        response = self.client.post(reverse('post-list'), {
            'title': 'Anon Post', 'content': 'Content',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated(self):
        token = get_token(self.client, 'creator', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('post-list'), {
            'title': 'My Post', 'content': 'Post content',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author']['username'], 'creator')

    def test_create_missing_title(self):
        token = get_token(self.client, 'creator', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('post-list'), {'content': 'No title'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PostUpdateDeleteTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='postauthor', password='pass1234')
        self.other = User.objects.create_user(username='other', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Original', content='Content'
        )

    def test_update_own_post(self):
        token = get_token(self.client, 'postauthor', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            reverse('post-detail', args=[self.post.pk]),
            {'title': 'Updated'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated')

    def test_update_other_post_forbidden(self):
        token = get_token(self.client, 'other', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            reverse('post-detail', args=[self.post.pk]),
            {'title': 'Hacked'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_anonymous_forbidden(self):
        response = self.client.patch(
            reverse('post-detail', args=[self.post.pk]),
            {'title': 'Anon'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_own_post(self):
        token = get_token(self.client, 'postauthor', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('post-detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_post_forbidden(self):
        token = get_token(self.client, 'other', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('post-detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_anonymous_forbidden(self):
        response = self.client.delete(reverse('post-detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostLikeActionTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='postowner', password='pass1234')
        self.liker = User.objects.create_user(username='liker', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Likeable Post', content='Content'
        )

    def _liker_token(self):
        return get_token(self.client, 'liker', 'pass1234')

    def test_like_post_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._liker_token()}')
        url = reverse('post-like', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'like added')

    def test_like_post_anonymous_forbidden(self):
        url = reverse('post-like', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unlike_post(self):
        PostLike.objects.create(post=self.post, user=self.liker)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._liker_token()}')
        url = reverse('post-like', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'like removed')

    def test_likes_count(self):
        PostLike.objects.create(post=self.post, user=self.liker)
        url = reverse('post-likes', args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

    def test_likes_count_not_found(self):
        url = reverse('post-likes', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostTopByLikesTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='topuser', password='pass1234')

    def test_top_by_likes_anonymous(self):
        url = reverse('post-top-by-likes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_top_by_likes_max_10(self):
        for i in range(15):
            Post.objects.create(author=self.user, title=f'Post {i}', content='c')
        url = reverse('post-top-by-likes')
        response = self.client.get(url)
        self.assertLessEqual(len(response.data), 10)

    def test_top_by_likes_ordered(self):
        p1 = Post.objects.create(author=self.user, title='Popular', content='c')
        p2 = Post.objects.create(author=self.user, title='Not popular', content='c')
        user2 = User.objects.create_user(username='liker2', password='pass')
        PostLike.objects.create(post=p1, user=self.user)
        PostLike.objects.create(post=p1, user=user2)
        PostLike.objects.create(post=p2, user=self.user)

        url = reverse('post-top-by-likes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], p1.pk)
        self.assertGreaterEqual(
            response.data[0]['likes_count'],
            response.data[1]['likes_count'],
        )

