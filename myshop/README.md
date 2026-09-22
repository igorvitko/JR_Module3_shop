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

## Frontend (React)

Окремий SPA у папці `frontend/` (Vite + React + React Router + axios).
У розробці ходить на бекенд через проксі `/api` (налаштовано в
`vite.config.js`) — CORS не заважає, хости збігаються з точки зору браузера.

```bash
cd frontend
npm install
npm run dev
```

Відкриється на <http://localhost:5173>. Бекенд (`docker compose up db` +
`uv run python manage.py runserver`, або повний `docker compose up`) має
бути запущений окремо — фронтенд поки не контейнеризований для розробки,
це свідоме рішення (додамо збірку в продакшн-інфраструктуру на Етапі 14).

**Що вже є:** роутинг (`react-router-dom`), axios-клієнт з автооновленням
JWT (`src/api/client.js`), контексти `AuthContext`/`CartContext`, базовий
layout (header/footer/nav), робочі сторінки логіну/реєстрації. Каталог,
картка товару, кошик і чекаут — плейсхолдери, наповнюються на Етапах 11–12.

## Статус реалізації

- [x] Етап 1 — Скелет проєкту, Docker (dev), налаштування dev/prod, CI-заглушка
- [x] Етап 2 — Моделі даних (Category, Product, Cart/CartItem, Order/OrderItem, Review, Profile)
- [x] Етап 3 — REST API каталогу (`/api/products/`, `/api/categories/`): фільтри, пошук, сортування, тести
- [x] Етап 4 — Відгуки (`/api/products/<id>/reviews/`) з перевіркою покупки, тести
- [x] Етап 5 — API кошика (`/api/cart/`): гостьовий токен, злиття при логіні, перевірка залишків, тести
- [x] Етап 6 — API користувачів: реєстрація, JWT логін/refresh, профіль, зміна пароля, тести
- [x] Етап 7 — API замовлень (`/api/orders/`): оформлення з кошика, транзакція зі списанням складу, email, скасування, тести
- [x] Етап 8 — Права доступу (IsOwner) та документація API (drf-spectacular: опис JWT-флоу, приклади запитів)
- [x] Етап 9 — Адмін-панель: аналітика (виторг/топ-товари/статуси), фільтри, масові дії, Profile вбудовано в User *(зроблено на крок раніше запланованого)*
- [x] Етап 10 — Скелет React: роутинг, axios-клієнт з auto-refresh JWT, layout, логін/реєстрація
- [x] Етап 11 — React: каталог (фільтри/пошук/сортування/пагінація в URL) і сторінка товару (кошик, відгуки)
- [x] Етап 12 — React: кошик, чекаут, особистий кабінет, історія замовлень зі скасуванням
- [ ] Етап 13 — Якість коду (типізація, лінтери, тести, покриття)
- [ ] Етап 5–6 — API кошика, користувачів
- [ ] Етап 7 — API замовлень, permissions, Swagger
- [ ] Етап 8 — Адмін-панель і аналітика
- [ ] Етап 9–12 — Frontend на React
- [ ] Етап 13–14 — Якість коду, prod-інфраструктура, фінальний README
- [ ] Етап 15 (бонус) — GraphQL
