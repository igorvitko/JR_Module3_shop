"""Спільні абстрактні моделі, які перевикористовуються в усіх застосунках."""
from django.db import models


class TimeStampedModel(models.Model):
    """Додає поля created_at / updated_at будь-якій моделі-нащадку."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        abstract = True
