from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Каталог товарів і категорій."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "products"
    verbose_name = "Товари"
