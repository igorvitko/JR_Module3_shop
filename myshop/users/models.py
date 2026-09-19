"""Модель профілю користувача.

Стандартна модель django.contrib.auth.User покриває реєстрацію/логін/
пароль. Profile додає поля, потрібні для особистого кабінету (Етап 6),
не чіпаючи вбудовану модель User.
"""
from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class Profile(TimeStampedModel):
    """Додаткові дані користувача, що не входять у стандартний User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Користувач",
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    default_shipping_address = models.TextField(
        blank=True, verbose_name="Адреса доставки за замовчуванням"
    )

    class Meta:
        verbose_name = "Профіль"
        verbose_name_plural = "Профілі"

    def __str__(self) -> str:
        return f"Профіль {self.user.username}"
