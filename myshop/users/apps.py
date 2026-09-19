from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Реєстрація, профіль користувача, JWT-автентифікація."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Користувачі"
