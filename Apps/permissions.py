from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return request.method in SAFE_METHODS

        if user.role == "basic_user" and not user.is_superuser:
            return request.method in SAFE_METHODS

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "author" and not user.is_superuser:
            return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return request.method in SAFE_METHODS

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "author" and not user.is_superuser:
            if obj.author.user.id == user.id:
                return True
            return request.method in SAFE_METHODS
        if user.role == "basic_user" and not user.is_superuser:
            return request.method in SAFE_METHODS
        return request.method in SAFE_METHODS


class IsAdminOrAuthorSpecificOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return request.method in SAFE_METHODS

        if user.role == "basic_user" and not user.is_superuser:
            return request.method in SAFE_METHODS

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "author" and not user.is_superuser:
            return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return request.method in SAFE_METHODS

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "author" and not user.is_superuser:
            if obj.user.id == user.id:
                return True
            return request.method in SAFE_METHODS
        if user.role == "basic_user" and not user.is_superuser:
            return request.method in SAFE_METHODS
        return request.method in SAFE_METHODS


class IsAdminOrReadOnly(BaseException):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return request.method in SAFE_METHODS
        if user.role == "admin" or user.is_superuser:
            return True
        if user.role in ["author", "basic_user"]:
            return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return request.method in SAFE_METHODS
        if user.role == "admin" or user.is_superuser:
            return True
        if user.role in ["author", "basic_user"]:
            return request.method in SAFE_METHODS


class IsAdminOrBuyerOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False
        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "basic_user":
            if request.method in ["POST", "GET", "PUT", "DELETE", "PATCH"]:
                return True
            return False
        if user.role == "author" and not user.is_superuser:
            return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "basic_user" and not user.is_superuser:
            if obj.user.id == user.id:
                return True
            return False
        if user.role == "author" and not user.is_superuser:
            return False


class IsAdminOrAuthorOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False
        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "author":
            if request.method in ["POST", "GET", "PUT", "DELETE", "PATCH"]:
                return True
            return False
        if user.role == "basic_user" and not user.is_superuser:
            return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role == "author" and not user.is_superuser:
            if obj.user.id == user.id:
                return True
            return False
        if user.role == "basic_user" and not user.is_superuser:
            return False


class IsAdminOrAuthorOrBuyerOnly(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated or request.user.is_anonymous:
            return False

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role in ["basic_user", "author"]:
            if request.method in ["POST"]:
                return False
            return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False

        if user.role == "admin" or user.is_superuser:
            return True
        if user.role in ["basic_user", "author"] and not user.is_superuser:
            if obj.id == user.id:
                return True
            return False


class IsAdminOrAnonymousOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return True
        if user.role == "admin" or user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(self, request, view)
