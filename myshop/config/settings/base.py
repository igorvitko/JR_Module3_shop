"""Спільні налаштування Django для всіх середовищ.

Середовище-специфічні налаштування (dev.py / prod.py) імпортують усе
звідси через `from .base import *` і перевизначають потрібні змінні.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Підвантажуємо змінні з .env у os.environ до того, як почнемо їх читати нижче.
# У Docker-контейнері .env передається через env_file/environment, тож цей
# виклик там просто нічого не знайде і мовчки пропуститься — це нормально.
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me-in-env")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонні застосунки
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    # Локальні застосунки проєкту
    "common",
    "products",
    "cart",
    "orders",
    "users",
    "reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Django-шаблони потрібні лише для вбудованої /admin/ панелі —
        # основний веб-інтерфейс реалізовано окремо на React (SPA),
        # який ходить у ті самі REST API, що й зовнішні клієнти.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "myshop"),
        "USER": os.environ.get("POSTGRES_USER", "myshop"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "myshop"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Django REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# --- JWT (simplejwt) ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- drf-spectacular (Swagger/OpenAPI) ---
SPECTACULAR_SETTINGS = {
    "TITLE": "Myshop API",
    "DESCRIPTION": """
REST API для інтернет-магазину Myshop (Django + DRF).

## Авторизація (JWT)

1. **Реєстрація**: `POST /api/users/register/` — username, email, password, password2.
2. **Логін**: `POST /api/users/login/` — username + password → `{"access": "...", "refresh": "..."}`.
3. Передавайте access-токен у заголовку кожного захищеного запиту:
   `Authorization: Bearer <access>`. Час життя — 15 хв.
4. Коли access протухне — `POST /api/users/login/refresh/` з `{"refresh": "..."}`
   поверне новий access (refresh живе 7 днів, ротується при кожному оновленні).

Натисніть **Authorize** вгорі цієї сторінки і вставте access-токен, щоб
тестувати захищені ендпоінти прямо тут.

## Кошик для неавторизованих користувачів

Кошик гостя ідентифікується заголовком `X-Cart-Token` (не JWT). Токен
повертається в кожній відповіді `/api/cart/` у полі `"token"` — збережіть
його (наприклад, у localStorage) і передавайте в наступних запитах. Коли
гість авторизується і передає той самий `X-Cart-Token`, кошик автоматично
зливається з постійним кошиком користувача.
""",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {"name": "Myshop"},
    "LICENSE": {"name": "MIT"},
}

# --- Email (перевизначається у dev.py / prod.py) ---
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@myshop.local")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
