from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Реєстрація, профіль користувача, JWT-автентифікація."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Користувачі"

    def ready(self) -> None:
        """Підключає сигнали застосунку при старті Django."""
        import users.signals  # noqa: F401
