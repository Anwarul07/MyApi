# # filters.py
import django_filters
from BookApp.models import Books
from CategoryApp.models import Category
from AuthorApp.models import Author
from UserApp.models import CustomUser
from CartApp.models import Cart
from Cartitem.models import CartItem


class BooksFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name="id", lookup_expr="exact")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    availability = django_filters.CharFilter(
        field_name="availability", lookup_expr="exact"
    )
    isbn = django_filters.CharFilter(field_name="isbn", lookup_expr="icontains")
    language = django_filters.CharFilter(field_name="language", lookup_expr="exact")
    binding_types = django_filters.CharFilter(
        field_name="binding_types", lookup_expr="exact"
    )
    publications = django_filters.CharFilter(
        field_name="publications", lookup_expr="icontains"
    )
    edition = django_filters.CharFilter(field_name="edition", lookup_expr="icontains")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(
        field_name="category__category_name", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="author__user__username", lookup_expr="icontains"
    )

    class Meta:
        model = Books
        fields = []


class AuthorFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name="id", lookup_expr="icontains")
    username = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    first_name = django_filters.CharFilter(
        field_name="user__first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(
        field_name="user__last_name", lookup_expr="icontains"
    )
    email = django_filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    mobile = django_filters.NumberFilter(
        field_name="user__mobile", lookup_expr="icontains"
    )
    is_verified = django_filters.BooleanFilter(
        field_name="is_verified", lookup_expr="exact"
    )

    class Meta:
        model = Author
        fields = []


class CategoryFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name="id", lookup_expr="exact")
    category = django_filters.CharFilter(
        field_name="category_name", lookup_expr="icontains"
    )
    origin = django_filters.CharFilter(field_name="origin", lookup_expr="icontains")

    class Meta:
        model = Category
        fields = []


### use some filter type to list them in view home


class Cartiemfilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name="id", lookup_expr="icontains")
    quantity = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="icontains"
    )
    books_title = django_filters.CharFilter(
        field_name="books__title", lookup_expr="icontains"
    )
    min_price = django_filters.NumberFilter(
        field_name="books__price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="books__price", lookup_expr="lte"
    )

    username = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    first_name = django_filters.CharFilter(
        field_name="user__first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(
        field_name="user__last_name", lookup_expr="icontains"
    )

    class Meta:
        models = CartItem
        fileds = []


class UserFilters(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name="id", lookup_expr="icontains")
    role = django_filters.CharFilter(field_name="role", lookup_expr="exact")
    username = django_filters.CharFilter(field_name="username", lookup_expr="icontains")
    first_name = django_filters.CharFilter(
        field_name="first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(
        field_name="last_name", lookup_expr="icontains"
    )
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    mobile = django_filters.NumberFilter(field_name="mobile", lookup_expr="icontains")

    class Meta:
        model = CustomUser
        fields = []



