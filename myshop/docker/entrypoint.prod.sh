#!/bin/sh
# Точка входу для продакшн-контейнера web. Запускається через
# `sh docker/entrypoint.prod.sh`, а не напряму (див. docker-compose.prod.yml) —
# так не залежимо від того, чи зберігся executable-біт файлу після
# копіювання з Windows-хоста в образ.
set -e

echo "Застосовуємо міграції..."
python manage.py migrate --noinput

echo "Збираємо статичні файли..."
python manage.py collectstatic --noinput

echo "Запускаємо gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
