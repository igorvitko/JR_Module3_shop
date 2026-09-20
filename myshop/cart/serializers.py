"""Серіалізатори кошика."""
from rest_framework import serializers

from cart.models import Cart, CartItem
from products.models import Product
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Позиція кошика для читання — з розгорнутими даними товару."""

    product = ProductListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "subtotal"]


class CartSerializer(serializers.ModelSerializer):
    """Кошик цілком: позиції, підсумкова сума, кількість одиниць, токен."""

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["token", "items", "total_price", "total_items"]


class CartItemWriteSerializer(serializers.Serializer):
    """Вхідні дані для додавання/оновлення позиції кошика (POST/PATCH/DELETE)."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)
