from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Post, Comment, PostLike, CommentLike
from .serializers import (
    UserSerializer,
    PostSerializer,
    CommentSerializer,
    PostLikeSerializer,
    CommentLikeSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'status': 'like removed'})
        return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        post = self.get_object()
        return Response({'likes_count': post.post_likes.count()})

    @action(detail=False, methods=['get'])
    def top_by_likes(self, request):
        posts = (
            Post.objects.annotate(likes_count=Count('post_likes'))
            .order_by('-likes_count', '-created_at')[:10]
        )
        data = [
            {
                'id': post.id,
                'title': post.title,
                'author_id': post.author_id,
                'likes_count': post.likes_count,
            }
            for post in posts
        ]
        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
        if not created:
            like.delete()
            return Response({'status': 'like removed'})
        return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        comment = self.get_object()
        return Response({'likes_count': comment.comment_likes.count()})

    @action(detail=False, methods=['get'])
    def top_by_likes(self, request):
        comments = (
            Comment.objects.annotate(likes_count=Count('comment_likes'))
            .order_by('-likes_count', '-created_at')[:10]
        )
        data = [
            {
                'id': comment.id,
                'post_id': comment.post_id,
                'author_id': comment.author_id,
                'likes_count': comment.likes_count,
            }
            for comment in comments
        ]
        return Response(data)


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
