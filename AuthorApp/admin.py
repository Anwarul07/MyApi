from django.contrib import admin
from AuthorApp.models import Author
from UserApp.models import CustomUser

# Register your models here.


# --- 2. Author Admin  ---
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = [
        "user",  # username
        "get_email",
        "get_mobile",
        "is_verified",
        "date_of_birth",
        "is_verified",
        "biography",
        "short_description",
        "date_of_birth",
        "user__cover_image",
        "user__front_image",
        "user__behind_image",
        "user__side_image",
        "user__top_image",
        "user__bottom_image",
    ]

    list_filter = ["is_verified"]
    search_fields = ["user__username", "user__email", "biography"]
    ordering = ["user__username"]

    fields = [
        "user",
        "is_verified",
        "biography",
        "short_description",
        "date_of_birth",
    ]

    # ---- Custom Display Methods ----
    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"

    def get_mobile(self, obj):
        return obj.user.mobile

    get_mobile.short_description = "Mobile"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(role="author")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
