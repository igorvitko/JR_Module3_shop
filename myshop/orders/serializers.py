"""Серіалізатори оформлення та перегляду замовлень."""
from decimal import Decimal

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import transaction

from rest_framework import serializers

from cart.models import Cart
from orders.models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    """Позиція замовлення — лише для читання (створюється лише сервером)."""

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """Замовлення для списку/деталей — усі поля лише для читання.

    Зміна статусу відбувається окремим шляхом (PATCH/DELETE на
    OrderViewSet), а не через прямий запис у це поле serializer'ом.
    """

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "payment_method",
            "total_price",
            "shipping_address",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Оформлення замовлення на основі поточного кошика авторизованого користувача."""

    shipping_address = serializers.CharField()
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices, default=Order.PaymentMethod.CARD
    )

    def validate(self, attrs: dict) -> dict:
        request = self.context["request"]
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            raise serializers.ValidationError(
                "Кошик порожній — немає що оформлювати в замовлення."
            )
        attrs["cart"] = cart
        return attrs

    @transaction.atomic
    def create(self, validated_data: dict) -> Order:
        request = self.context["request"]
        cart: Cart = validated_data["cart"]
        cart_items = list(cart.items.select_related("product"))

        # select_for_update блокує рядки товарів до кінця транзакції —
        # без цього два паралельні замовлення могли б обидва пройти
        # перевірку стоку і в сумі продати більше, ніж є на складі.
        locked_products = {
            product.pk: product
            for product in Product.objects.select_for_update().filter(
                pk__in=[item.product_id for item in cart_items]
            )
        }

        for item in cart_items:
            product = locked_products[item.product_id]
            if item.quantity > product.stock:
                raise serializers.ValidationError(
                    f"Недостатньо товару «{product.name}» на складі "
                    f"(доступно {product.stock}, потрібно {item.quantity})."
                )

        total_price = sum(
            (
                locked_products[item.product_id].price * item.quantity
                for item in cart_items
            ),
            start=Decimal("0"),
        )

        order = Order.objects.create(
            user=request.user,
            shipping_address=validated_data["shipping_address"],
            payment_method=validated_data["payment_method"],
            total_price=total_price,
        )

        for item in cart_items:
            product = locked_products[item.product_id]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=item.quantity,
                price=product.price,
            )
            product.stock -= item.quantity
            product.save(update_fields=["stock"])

        cart.items.all().delete()
        self._send_order_notifications(order)
        return order

    @staticmethod
    def _send_order_notifications(order: Order) -> None:
        """Надсилає лист покупцю та (за наявності ADMIN_EMAIL) адміністратору.

        У dev листи не йдуть насправді — EMAIL_BACKEND виводить їх у
        консоль контейнера (config/settings/dev.py).
        """
        if order.user.email:
            send_mail(
                subject=f"Замовлення #{order.id} прийнято",
                message=(
                    f"Дякуємо за замовлення #{order.id} на суму "
                    f"{order.total_price} грн. Статус: {order.get_status_display()}."
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                fail_silently=True,
            )

        if django_settings.ADMIN_EMAIL:
            send_mail(
                subject=f"Нове замовлення #{order.id}",
                message=(
                    f"Користувач {order.user.username} оформив замовлення "
                    f"на суму {order.total_price} грн."
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[django_settings.ADMIN_EMAIL],
                fail_silently=True,
            )
