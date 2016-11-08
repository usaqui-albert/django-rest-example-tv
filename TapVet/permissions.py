from rest_framework.permissions import BasePermission


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
