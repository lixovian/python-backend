from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lix.models import Post, Comment, CommentLike


def get_token(client, username, password):
    response = client.post(reverse('token_obtain_pair'), {
        'username': username, 'password': password,
    })
    return response.data.get('access')


class CommentListRetrieveTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='commenter', password='pass1234')
        self.post = Post.objects.create(author=self.user, title='Post', content='Content')
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content='Nice post!'
        )

    def test_list_anonymous(self):
        response = self.client.get(reverse('comment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_anonymous(self):
        response = self.client.get(reverse('comment-detail', args=[self.comment.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Nice post!')

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('comment-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentCreateTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass1234')
        self.post = Post.objects.create(author=self.user, title='Post', content='Content')

    def test_create_anonymous_forbidden(self):
        response = self.client.post(reverse('comment-list'), {
            'post': self.post.pk,
            'content': 'Anonymous comment',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated(self):
        token = get_token(self.client, 'creator', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('comment-list'), {
            'post': self.post.pk,
            'content': 'My comment',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author']['username'], 'creator')

    def test_create_missing_content(self):
        token = get_token(self.client, 'creator', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('comment-list'), {'post': self.post.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_post(self):
        token = get_token(self.client, 'creator', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('comment-list'), {'content': 'No post ref'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_nonexistent_post(self):
        token = get_token(self.client, 'creator', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('comment-list'), {
            'post': 99999,
            'content': 'Comment on void',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentUpdateDeleteTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='comauthor', password='pass1234')
        self.other = User.objects.create_user(username='comother', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Post', content='Content'
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.author, content='Original comment'
        )

    def test_update_own_comment(self):
        token = get_token(self.client, 'comauthor', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            reverse('comment-detail', args=[self.comment.pk]),
            {'content': 'Updated comment'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated comment')

    def test_update_other_comment_forbidden(self):
        token = get_token(self.client, 'comother', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            reverse('comment-detail', args=[self.comment.pk]),
            {'content': 'Hacked'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_anonymous_forbidden(self):
        response = self.client.patch(
            reverse('comment-detail', args=[self.comment.pk]),
            {'content': 'Anon'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_own_comment(self):
        token = get_token(self.client, 'comauthor', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('comment-detail', args=[self.comment.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_comment_forbidden(self):
        token = get_token(self.client, 'comother', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('comment-detail', args=[self.comment.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_anonymous_forbidden(self):
        response = self.client.delete(reverse('comment-detail', args=[self.comment.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentLikeActionTests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='comowner', password='pass1234')
        self.liker = User.objects.create_user(username='comliker', password='pass1234')
        self.post = Post.objects.create(
            author=self.author, title='Post', content='Content'
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.author, content='Comment'
        )

    def _liker_token(self):
        return get_token(self.client, 'comliker', 'pass1234')

    def test_like_comment_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._liker_token()}')
        url = reverse('comment-like', args=[self.comment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'like added')

    def test_like_comment_anonymous_forbidden(self):
        url = reverse('comment-like', args=[self.comment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unlike_comment(self):
        CommentLike.objects.create(comment=self.comment, user=self.liker)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._liker_token()}')
        url = reverse('comment-like', args=[self.comment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'like removed')

    def test_likes_count(self):
        CommentLike.objects.create(comment=self.comment, user=self.liker)
        url = reverse('comment-likes', args=[self.comment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

    def test_likes_count_not_found(self):
        url = reverse('comment-likes', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentTopByLikesTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='topcomuser', password='pass1234')
        self.post = Post.objects.create(
            author=self.user, title='Post', content='Content'
        )

    def test_top_by_likes_anonymous(self):
        url = reverse('comment-top-by-likes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_top_by_likes_max_10(self):
        for i in range(15):
            Comment.objects.create(
                post=self.post, author=self.user, content=f'Comment {i}'
            )
        url = reverse('comment-top-by-likes')
        response = self.client.get(url)
        self.assertLessEqual(len(response.data), 10)

    def test_top_by_likes_ordered(self):
        c1 = Comment.objects.create(
            post=self.post, author=self.user, content='Popular comment'
        )
        c2 = Comment.objects.create(
            post=self.post, author=self.user, content='Less popular'
        )
        user2 = User.objects.create_user(username='liker3', password='pass')
        CommentLike.objects.create(comment=c1, user=self.user)
        CommentLike.objects.create(comment=c1, user=user2)
        CommentLike.objects.create(comment=c2, user=self.user)

        url = reverse('comment-top-by-likes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], c1.pk)
        self.assertGreaterEqual(
            response.data[0]['likes_count'],
            response.data[1]['likes_count'],
        )

