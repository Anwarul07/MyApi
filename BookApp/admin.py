from django.contrib import admin
from BookApp.models import Books
from AuthorApp.models import Author


# --- 2. Books Admin  ---
@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "author_name",
        "category_name",
        "isbn",
        "price",
        "discount",
        "sale_price",
        "availability",
        "language",
        "cover_image",
        "front_image",
        "behind_image",
        "side_image",
        "top_image",
        "bottom_image",
    ]
    list_display_links = ["title"]

    list_filter = [
        "author",
        "category",
        "availability",
        "language",
        "binding_types",
        "edition",
        "publication_date",
    ]

    search_fields = [
        "title",
        "isbn",
        "description",
        "summary",
        "author__user__username",
        "category__category_name",
    ]

    ordering = ["title"]

    readonly_fields = [
        "created_at",
        "updated_at",
        "sale_price",
    ]

    fieldsets = (
        (
            "Book Details",
            {
                "fields": (
                    "title",
                    "author",
                    "category",
                    "total_pages",
                    "isbn",
                    "ratings",
                    "publication_date",
                )
            },
        ),
        (
            "Images",
            {
                "fields": (
                    "cover_image",
                    "front_image",
                    "behind_image",
                    "side_image",
                    "top_image",
                    "bottom_image",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "discount",
                    "sale_price",
                )
            },
        ),
        (
            "Extra Info",
            {
                "fields": (
                    "publications",
                    "availability",
                    "language",
                    "binding_types",
                    "edition",
                    "description",
                    "summary",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # Custom display fields
    def author_name(self, obj):
        return f"{obj.author.user.first_name} {obj.author.user.last_name}"

    def category_name(self, obj):
        return obj.category.category_name

    def sale_price(self, obj):
        return obj.sale_price

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            # Only Author role  users will show
            from AuthorApp.models import Author

            kwargs["queryset"] = Author.objects.filter(user__role="author")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
