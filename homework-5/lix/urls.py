from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    PostViewSet,
    CommentViewSet,
    PostLikeViewSet,
    CommentLikeViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'post-likes', PostLikeViewSet)
router.register(r'comment-likes', CommentLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
