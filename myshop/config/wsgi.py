"""WSGI-конфігурація для проєкту myshop.

Використовується gunicorn у продакшн-контейнері. За замовчуванням
вказує на продакшн-налаштування; для локального запуску через
`manage.py runserver` використовується config.settings.dev (див. manage.py).
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
