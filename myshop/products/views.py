"""API-view каталогу товарів."""
from django.db.models import Avg, Count, QuerySet

from rest_framework import viewsets

from products.filters import ProductFilter
from products.models import Category, Product
from products.serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Каталог товарів: список (фільтри/пошук/сортування/пагінація) і деталі.

    Тільки читання — товари створюються/редагуються через Django Admin
    (Етап 9), REST API каталогу призначений для клієнтів (React, зовнішні
    інтеграції).
    """

    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "popularity"]
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet[Product]:
        # select_related уникає N+1 при зверненні до product.category.
        # Count(..., distinct=True) обов'язковий: без нього одночасна
        # анотація Avg по reviews і Count по order_items дає декартів
        # добуток рядків (fan-out join) і Count порахує зайві дублікати.
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .annotate(
                average_rating_annotated=Avg("reviews__rating"),
                popularity=Count("order_items", distinct=True),
            )
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Список категорій — потрібен фронтенду для побудови фільтрів каталогу."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # категорій мало, пагінація не потрібна
