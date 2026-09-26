"""Налаштування для продакшн-середовища.

Усе, що тут не задане "жорстко", очікується у змінних оточення
(див. .env.example) — контейнер отримує їх через docker-compose.prod.yml.
"""
import os

from .base import *  # noqa: F401,F403

DEBUG = False

# Стиснене сховище з маніфестом — лише для prod, де перед запуском
# гарантовано виконується `collectstatic` (див. Dockerfile/entrypoint,
# буде додано на Етапі 14). У dev цей маніфест не генерується, і будь-яка
# сторінка з {% static %} (наприклад, /admin/) впала б з ValueError.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

# --- Безпека ---
# УВАГА: docker-compose.prod.yml + nginx у цьому проєкті обслуговують
# лише звичайний HTTP (порт 80) — TLS-сертифікат не налаштований (для
# цього потрібен реальний домен і, наприклад, certbot/Let's Encrypt —
# поза межами обсягу навчального проєкту). Тому ці прапорці за
# замовчуванням ВИМКНЕНІ: SECURE_SSL_REDIRECT=True без реального HTTPS
# створив би нескінченний редирект, а *_COOKIE_SECURE=True — робив би
# сесію/CSRF-кукі непрацюючими (браузер не надсилає їх по HTTP).
#
# Якщо деплоїте за реальним доменом із TLS (nginx+certbot або хмарний
# балансувальник із HTTPS) — увімкніть усе це через .env:
#   DJANGO_SECURE_SSL_REDIRECT=True
#   DJANGO_SESSION_COOKIE_SECURE=True
#   DJANGO_CSRF_COOKIE_SECURE=True
#   DJANGO_SECURE_HSTS_SECONDS=2592000
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = os.environ.get("DJANGO_SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE = os.environ.get("DJANGO_CSRF_COOKIE_SECURE", "False") == "True"
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0

# --- Email (реальний SMTP) ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
