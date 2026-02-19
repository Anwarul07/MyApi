from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
from CategoryApp.models import Category
from AuthorApp.models import Author


# ---------------- Book Categoty Serializer for Category details----------------


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex", read_only=True)
    totalbook = serializers.SerializerMethodField()
    totalauthors = serializers.SerializerMethodField()

    # category_of_books = serializers.SerializerMethodField() --->
    # authors = serializers.SerializerMethodField() --->

    class Meta:
        model = Category
        fields = "__all__"

        read_only_fields = [
            "totalbook",
            "totalauthors",
            "created_at",
            "updated_at",
            # "authors", --->
            # "category_of_books", --->
        ]

    def get_totalbook(self, obj):
        return obj.category_of_books.count()

    def get_totalauthors(self, obj):
        return obj.category_of_books.values_list("author", flat=True).distinct().count()
    
    

    # def get_category_of_books(self, obj):
    #     from BookApp.serializers import BooksReadSerializer

    #     books = obj.category_of_books.all()
    #     return BooksReadSerializer(books, many=True, context=self.context).data

    # def get_authors(self, obj):
    #     data = authors_qs = (
    #         Author.objects.filter(books_of_author__category=obj)
    #         .distinct()
    #         .select_related("user")
    #     )
    #     unique_authors = [
    #         {
    #             "user_id": author.user.id,
    #             "first_name": author.user.first_name,
    #             "last_name": author.user.last_name,
    #             "email": author.user.email,
    #         }
    #         for author in data
    #     ]

    #     return unique_authors
