from rest_framework import permissions


class IsSuperUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous is True:
            return False
        return request.user.is_superuser is True


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous is True:
            return False
        return request.user.is_admin is True


class IsLeadPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous is True:
            return False
        return request.user.is_lead is True


class TransactionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous is True:
            return False
        return request.user.is_lead is True or request.user.is_admin is True
