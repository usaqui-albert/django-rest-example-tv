from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsVet(BasePermission):
    message = 'Error: You dont have permission to view'

    def has_permission(self, request, view):

        if not request.user.is_authenticated():
            return False

        return (
            request.user.has_perm('users.is_vet') or
            request.user.is_staff
        )


class IsPetOwner(BasePermission):
    message = 'Error: You dont have permission to view'

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        return (
            request.user.has_perm('users.is_pet_owner') or
            request.user.is_staff
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        elif request.user and request.user.is_authenticated():
            # request user must be equal to obj user or request user is staff.
            return obj.user_id == request.user.id or request.user.is_staff
        else:
            return False
