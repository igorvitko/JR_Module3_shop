from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Відгуки та рейтинги товарів."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "reviews"
    verbose_name = "Відгуки"
