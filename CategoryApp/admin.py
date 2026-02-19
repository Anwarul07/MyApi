from django.contrib import admin
from CategoryApp.models import Category

# Register your models here.


# --- 3. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "category_name",
        "description",
        "cover_image",
        "front_image",
        "behind_image",
        "side_image",
        "top_image",
        "bottom_image",
        "origin",
    ]
    list_filter = ["origin"]
    search_fields = ["category_name", "description"]
    ordering = ["category_name"]

    list_display_links = ["category_name"]
    list_editable = ["origin"]

    # Form's fields  order
    fields = [
        "category_name",
        "cover_image",
        "front_image",
        "behind_image",
        "side_image",
        "top_image",
        "bottom_image",
        "description",
        "origin",
    ]
