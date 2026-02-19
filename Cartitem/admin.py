from django.contrib import admin
from Cartitem.models import CartItem



# Register your models here.

# --- 4. CartItem Admin ---
@admin.register(CartItem)
class CartItemStandaloneAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "books", "quantity", "added_at"]
    list_filter = ["user", "books"]
    search_fields = ["user__username", "books__title"]
    readonly_fields = ["added_at"]
    ordering = ["-added_at"]
    list_editable = ["quantity"]

    # autocomplete_fields = ["user", "books"]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from UserApp.models import CustomUser

        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(role="basic_user")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
