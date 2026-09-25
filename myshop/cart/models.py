"""Моделі кошика покупця.

Кошик ідентифікується або токеном (для гостей — токен зберігається у
localStorage на фронтенді та передається в заголовку/параметрі запиту),
або прив'язкою до користувача (після логіну). Ця модель зберігається в
БД (а не в django-сесії), бо фронтенд — окремий React SPA, який ходить
у REST API так само, як і зовнішні клієнти.
"""
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel
from products.models import Product


class Cart(TimeStampedModel):
    """Кошик — або гостьовий (за токеном), або прив'язаний до user."""

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Токен кошика",
        help_text="Використовується для ідентифікації кошика гостя.",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
        verbose_name="Користувач",
        help_text="Порожньо для гостьового кошика.",
    )

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"

    def __str__(self) -> str:
        if self.user is not None:
            return f"Кошик ({self.user.username})"
        return f"Кошик (гість {self.token})"

    @property
    def total_price(self) -> Decimal:
        """Сума вартості всіх позицій кошика."""
        return sum((item.subtotal for item in self.items.all()), start=Decimal("0"))

    @property
    def total_items(self) -> int:
        """Загальна кількість одиниць товару в кошику."""
        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    """Одна позиція товару в кошику."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    class Meta:
        verbose_name = "Позиція кошика"
        verbose_name_plural = "Позиції кошика"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_product_per_cart"
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        """Вартість цієї позиції (ціна товару * кількість)."""
        return self.product.price * self.quantity
