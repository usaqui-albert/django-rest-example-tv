from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """
    message = 'Error: You dont have permission to edit'

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if not request.user.is_authenticated():
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return obj.id == request.user.id or request.user.is_staff
