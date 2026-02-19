from .models import Cart
from django.contrib import admin


# Register your models here.


# --- 4. Cart Admin  ---
@admin.register(Cart)
class CartStandaloneAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "user_email", "user_mobile"]
    search_fields = ["user__username", "user__email", "user__mobile"]
    list_filter = ["user"]
    ordering = ["user__username"]
    list_display_links = ["user"]

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Mobile")
    def user_mobile(self, obj):
        return obj.user.mobile

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            from UserApp.models import CustomUser

            kwargs["queryset"] = CustomUser.objects.filter(role="basic_user")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
