# Myshop — інтернет-магазин (Django + DRF + React)

> Проєкт перебуває в активній розробці за поетапним планом. Цей README буде
> доповнено повною документацією (API, JWT, тести, деплой) на фінальному етапі.

## Стек

- **Backend:** Django, Django REST Framework, JWT (simplejwt), PostgreSQL
- **Frontend:** React (буде додано на Етапі 10, папка `frontend/`)
- **Пакетний менеджер:** [uv](https://docs.astral.sh/uv/)
- **Інфраструктура:** Docker, Docker Compose
- **CI:** GitHub Actions (flake8, mypy, pytest)

## Швидкий старт (локальна розробка)

1. Скопіюйте `.env.example` у `.env` і за потреби змініть значення:

   ```bash
   cp .env.example .env
   ```

2. Запустіть проєкт через Docker Compose:

   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

3. Застосунок буде доступний на <http://localhost:8000>.
   Перевірити, що все живе, можна на <http://localhost:8000/api/health/>.

4. Документація API (Swagger): <http://localhost:8000/api/docs/>

### Локально без Docker (опційно)

```bash
uv sync --all-groups
uv run python manage.py migrate
uv run python manage.py runserver
```

Потрібна локально запущена PostgreSQL, параметри підключення — у `.env`.

## Тести та лінтери

```bash
uv run pytest        # тести
uv run flake8 .       # лінтер стилю
uv run mypy .         # перевірка типізації
```

## Структура проєкту (поточний стан)

```
myshop/
├── config/          # Налаштування Django (settings/base|dev|prod.py), urls, wsgi/asgi
├── common/          # Спільні утиліти (health-check тощо)
├── products/        # Каталог товарів і категорій
├── cart/            # Кошик покупця
├── orders/          # Оформлення та історія замовлень
├── users/           # Реєстрація, профіль, автентифікація
├── reviews/         # Відгуки та рейтинги
├── docker-compose.dev.yml
├── Dockerfile
├── pyproject.toml   # Залежності (uv)
└── manage.py
```

Моделі, API-ендпоінти, адмінка та фронтенд додаються поетапно —
детальний план розробки веде викладач/розробник окремо.

## Статус реалізації

- [x] Етап 1 — Скелет проєкту, Docker (dev), налаштування dev/prod, CI-заглушка
- [x] Етап 2 — Моделі даних (Category, Product, Cart/CartItem, Order/OrderItem, Review, Profile)
- [x] Етап 3 — REST API каталогу (`/api/products/`, `/api/categories/`): фільтри, пошук, сортування, тести
- [ ] Етап 4 — API товару та відгуків (`/api/products/<id>/reviews/`)
- [ ] Етап 5–6 — API кошика, користувачів
- [ ] Етап 7 — API замовлень, permissions, Swagger
- [ ] Етап 8 — Адмін-панель і аналітика
- [ ] Етап 9–12 — Frontend на React
- [ ] Етап 13–14 — Якість коду, prod-інфраструктура, фінальний README
- [ ] Етап 15 (бонус) — GraphQL
