from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Спільні утиліти та допоміжні view, що не належать конкретному домену."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "common"
    verbose_name = "Загальне"
