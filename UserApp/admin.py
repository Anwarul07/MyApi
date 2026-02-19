from django.contrib import admin
from UserApp.models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.


# --- 1. Custom User  ---


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # --- List view ---
    list_display = (
        "username",
        "email",
        "role",
        "mobile",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
        "last_login",
        "cover_image",
        "front_image",
        "behind_image",
        "side_image",
        "top_image",
        "bottom_image",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "mobile")
    ordering = ("username",)
    list_editable = ("role", "is_active")  # optional quick edit

    # --- Read-only fields ---
    readonly_fields = ("date_joined", "last_login")

    # --- Edit form ---
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Role & Contact Info",
            {
                "fields": ("role", "mobile"),
            },
        ),
        (
            "User Images",
            {
                "fields": (
                    "cover_image",
                    "front_image",
                    "behind_image",
                    "side_image",
                    "top_image",
                    "bottom_image",
                ),
                "classes": ("collapse",),  # collapsible in admin
            },
        ),
    )

    # --- Add new user form ---
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Role & Contact Info",
            {
                "fields": ("role", "mobile"),
            },
        ),
        (
            "User Images",
            {
                "fields": (
                    "cover_image",
                    "front_image",
                    "behind_image",
                    "side_image",
                    "top_image",
                    "bottom_image",
                ),
            },
        ),
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # Restrict users shown in autocomplete
        queryset = queryset.filter(role="basic_user")
        return queryset, use_distinct
