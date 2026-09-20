"""Фільтри каталогу товарів (django-filter)."""
import django_filters

from products.models import Product


class ProductFilter(django_filters.FilterSet):
    """Фільтрація списку товарів за категорією та діапазоном цін.

    Пошук (?search=) та сортування (?ordering=) підключені окремо через
    SearchFilter / OrderingFilter (див. DEFAULT_FILTER_BACKENDS у settings
    та атрибути search_fields / ordering_fields на ProductViewSet).
    """

    category = django_filters.NumberFilter(
        field_name="category_id", help_text="ID категорії."
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]
