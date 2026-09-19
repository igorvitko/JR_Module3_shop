"""Модель відгуків на товари."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import TimeStampedModel
from products.models import Product


class Review(TimeStampedModel):
    """Відгук користувача на товар.

    Бізнес-правило "залишити відгук можна лише після покупки товару"
    перевіряється на рівні API (Етап 4), а не тут — модель відповідає
    лише за структуру даних та цілісність (один відгук на товар від
    одного користувача).
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Рейтинг",
    )
    comment = models.TextField(blank=True, verbose_name="Коментар")

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"], name="unique_review_per_user_product"
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.name} — {self.rating}/5 від {self.user.username}"
