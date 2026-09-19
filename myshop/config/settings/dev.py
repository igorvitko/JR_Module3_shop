"""Налаштування для локальної розробки."""
from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# У dev дозволяємо запити з фронтенду (Vite dev server) без обмежень.
CORS_ALLOW_ALL_ORIGINS = True

# Листи не надсилаються насправді, а виводяться в консоль контейнера web.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Зручний дебаг довгих SQL-запитів під час розробки.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
