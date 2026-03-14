from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import User


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if isinstance(obj, User):
            return obj == request.user or request.user.is_staff
        if hasattr(obj, 'author'):
            return obj.author == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
