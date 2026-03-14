from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lix.models import Post, Comment, PostLike, CommentLike

def get_token(client, username, password):
    response = client.post(reverse('token_obtain_pair'), {
        'username': username, 'password': password,
    })
    return response.data.get('access')


class PostLikeViewSetTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='plauthor', password='pass1234')
        self.liker = User.objects.create_user(username='plliker', password='pass1234')
        self.other = User.objects.create_user(username='plother', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Post', content='Content'
        )

    def test_list_anonymous(self):
        response = self.client.get(reverse('postlike-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_anonymous_forbidden(self):
        response = self.client.post(reverse('postlike-list'), {'post': self.post.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated(self):
        token = get_token(self.client, 'plliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('postlike-list'), {'post': self.post.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'plliker')

    def test_create_duplicate_like_forbidden(self):
        PostLike.objects.create(post=self.post, user=self.liker)
        token = get_token(self.client, 'plliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('postlike-list'), {'post': self.post.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_like(self):
        like = PostLike.objects.create(post=self.post, user=self.liker)
        response = self.client.get(reverse('postlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_own_like(self):
        like = PostLike.objects.create(post=self.post, user=self.liker)
        token = get_token(self.client, 'plliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('postlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_like_forbidden(self):
        like = PostLike.objects.create(post=self.post, user=self.liker)
        token = get_token(self.client, 'plother', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('postlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_anonymous_forbidden(self):
        like = PostLike.objects.create(post=self.post, user=self.liker)
        response = self.client.delete(reverse('postlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_found(self):
        token = get_token(self.client, 'plliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('postlike-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentLikeViewSetTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='clauthor', password='pass1234')
        self.liker = User.objects.create_user(username='clliker', password='pass1234')
        self.other = User.objects.create_user(username='clother', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Post', content='Content'
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.author, content='Comment'
        )

    def test_list_anonymous(self):
        response = self.client.get(reverse('commentlike-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_anonymous_forbidden(self):
        response = self.client.post(
            reverse('commentlike-list'), {'comment': self.comment.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated(self):
        token = get_token(self.client, 'clliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            reverse('commentlike-list'), {'comment': self.comment.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'clliker')

    def test_create_duplicate_like_forbidden(self):
        CommentLike.objects.create(comment=self.comment, user=self.liker)
        token = get_token(self.client, 'clliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            reverse('commentlike-list'), {'comment': self.comment.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_like(self):
        like = CommentLike.objects.create(comment=self.comment, user=self.liker)
        response = self.client.get(reverse('commentlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_own_like(self):
        like = CommentLike.objects.create(comment=self.comment, user=self.liker)
        token = get_token(self.client, 'clliker', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('commentlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_like_forbidden(self):
        like = CommentLike.objects.create(comment=self.comment, user=self.liker)
        token = get_token(self.client, 'clother', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('commentlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_anonymous_forbidden(self):
        like = CommentLike.objects.create(comment=self.comment, user=self.liker)
        response = self.client.delete(reverse('commentlike-detail', args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

