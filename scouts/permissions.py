from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from scouts.models import Scout


class IsScout(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and Scout.objects.filter(user=request.user):
            return True
        return False
