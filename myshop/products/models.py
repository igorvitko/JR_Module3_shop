"""Моделі каталогу товарів: категорії (з вкладеністю) та товари."""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from common.models import TimeStampedModel


class Category(TimeStampedModel):
    """Категорія товарів з підтримкою довільної вкладеності (self-FK)."""

    name = models.CharField(max_length=150, verbose_name="Назва")
    slug = models.SlugField(max_length=170, unique=True, verbose_name="Слаг")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Батьківська категорія",
        help_text="Залиште порожнім для категорії верхнього рівня.",
    )

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    """Товар каталогу."""

    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(max_length=280, unique=True, verbose_name="Слаг")
    description = models.TextField(blank=True, verbose_name="Опис")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Ціна",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категорія",
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Зображення",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний",
        help_text="Неактивні товари не показуються в каталозі та пошуку.",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Залишок на складі")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "category"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_in_stock(self) -> bool:
        """Чи є товар в наявності (для перевірок у кошику/замовленні)."""
        return self.stock > 0

    @property
    def average_rating(self) -> float | None:
        """Середній рейтинг за відгуками; None, якщо відгуків ще немає."""
        aggregate = self.reviews.aggregate(models.Avg("rating"))
        return aggregate["rating__avg"]
