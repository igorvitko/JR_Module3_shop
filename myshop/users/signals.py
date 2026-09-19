"""Сигнали застосунку users."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created: bool, **kwargs) -> None:
    """Автоматично створює Profile одразу після реєстрації користувача."""
    if created:
        Profile.objects.create(user=instance)
