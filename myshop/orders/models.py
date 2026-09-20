"""Моделі замовлень."""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from common.models import TimeStampedModel
from products.models import Product


class Order(TimeStampedModel):
    """Замовлення користувача.

    Створюється на основі кошика під час чекауту (Етап 7). Оформлення
    замовлення вимагає авторизації — гостьового чекауту ТЗ не передбачає.
    """

    class Status(models.TextChoices):
        """Статуси життєвого циклу замовлення."""

        PENDING = "pending", "Очікує оплати"
        PAID = "paid", "Оплачено"
        SHIPPED = "shipped", "Відправлено"
        DELIVERED = "delivered", "Доставлено"
        CANCELLED = "cancelled", "Скасовано"

    class PaymentMethod(models.TextChoices):
        """Спосіб оплати. Реальної інтеграції з платіжним провайдером немає —
        це імітація/мок, як прямо дозволяє ТЗ (розділ 3.4)."""

        CARD = "card", "Оплата карткою (мок)"
        CASH_ON_DELIVERY = "cash_on_delivery", "Оплата при отриманні"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Користувач",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        verbose_name="Спосіб оплати",
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Загальна сума",
    )
    shipping_address = models.TextField(verbose_name="Адреса доставки")

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self) -> str:
        return f"Замовлення #{self.pk} ({self.get_status_display()})"

    @property
    def can_be_cancelled(self) -> bool:
        """Скасувати можна лише замовлення, яке ще не відправлене."""
        return self.status in {self.Status.PENDING, self.Status.PAID}


class OrderItem(TimeStampedModel):
    """Позиція замовлення зі знімком ціни та назви товару на момент купівлі.

    product може стати NULL, якщо товар згодом видалять з каталогу —
    product_name і price зберігають історичну інформацію незалежно від
    того, чи існує ще сам товар.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    product_name = models.CharField(
        max_length=255,
        verbose_name="Назва товару",
        help_text="Знімок назви на момент замовлення.",
    )
    quantity = models.PositiveIntegerField(verbose_name="Кількість")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна за одиницю",
        help_text="Знімок ціни товару на момент покупки.",
    )

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        """Вартість цієї позиції (знімок ціни * кількість)."""
        return self.price * self.quantity
