"""Серіалізатори каталогу товарів."""
from rest_framework import serializers

from products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Категорія — використовується як окремий ендпоінт для фільтрів фронтенду."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent"]


class ProductListSerializer(serializers.ModelSerializer):
    """Полегшений серіалізатор для списку товарів (каталог, пошук)."""

    average_rating = serializers.FloatField(
        source="average_rating_annotated", read_only=True, allow_null=True
    )
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "category",
            "image",
            "stock",
            "is_in_stock",
            "average_rating",
        ]


class ProductDetailSerializer(ProductListSerializer):
    """Повний серіалізатор для сторінки товару — з вкладеною категорією й описом."""

    category = CategorySerializer(read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            "description",
            "created_at",
            "updated_at",
        ]
