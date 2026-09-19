from django.apps import AppConfig


class CartConfig(AppConfig):
    """Кошик покупця.

    Реалізований окремо від orders: кошик ідентифікується токеном
    (для гостей — cookie/localStorage на фронтенді, для авторизованих —
    прив'язкою до user), тоді як orders — це вже завершені замовлення.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
    verbose_name = "Кошик"
