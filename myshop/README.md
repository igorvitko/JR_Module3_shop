# Myshop — інтернет-магазин (Django + DRF + React)

Навчальний проєкт: повноцінний інтернет-магазин з REST API на Django REST
Framework, JWT-авторизацією та SPA-фронтендом на React.

## Стек

- **Backend:** Django 5, Django REST Framework, JWT (`djangorestframework-simplejwt`), PostgreSQL
- **Frontend:** React 18 + Vite, React Router, axios
- **Документація API:** drf-spectacular (Swagger/OpenAPI)
- **Пакетний менеджер (backend):** [uv](https://docs.astral.sh/uv/)
- **Інфраструктура:** Docker, Docker Compose (окремі конфігурації для dev і prod), nginx
- **Якість коду:** flake8, mypy (django-stubs), pytest + pytest-django + pytest-cov
- **CI:** GitHub Actions (лінтери + тести з покриттям на кожен push/PR)

## Швидкий старт (локальна розробка)

1. Скопіюйте `.env.example` у `.env`:

   ```bash
   cp .env.example .env
   ```

2. Запустіть бекенд через Docker Compose (Django + PostgreSQL):

   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

   Застосунок буде доступний на <http://localhost:8000>, health-check —
   на <http://localhost:8000/api/health/>, Swagger — на
   <http://localhost:8000/api/docs/>.

   Альтернатива без повного Docker (PostgreSQL у контейнері, Django —
   нативно через uv; швидший цикл розробки):

   ```bash
   docker compose -f docker-compose.dev.yml up db
   uv sync --all-groups
   uv run python manage.py migrate
   uv run python manage.py loaddata initial_products   # тестові дані каталогу
   uv run python manage.py createsuperuser
   uv run python manage.py runserver
   ```

3. Запустіть фронтенд (окремий термінал):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Відкриється на <http://localhost:5173> і ходитиме на бекенд через проксі
   `/api` (див. `frontend/vite.config.js`) — CORS не заважає.

## Продакшн-запуск (Docker Compose)

Продакшн-стек — три сервіси: `db` (PostgreSQL), `web` (Django під gunicorn),
`nginx` (роздає зібраний React і проксіює `/api/`, `/admin/` на `web`).
React збирається в статику всередині Docker-образу nginx — окремо
запускати `npm run build` не потрібно.

1. Підготуйте `.env` (той самий файл, що й для dev, але зверніть увагу на
   продакшн-специфічні змінні — коментарі прямо в `.env.example`):
   - `DJANGO_SETTINGS_MODULE=config.settings.prod`
   - `DJANGO_ALLOWED_HOSTS` — реальний домен/IP сервера
   - `DJANGO_SECRET_KEY` — новий, згенерований, не той, що в dev
   - За замовчуванням сайт піднімається по звичайному HTTP (порт 80, без
     TLS-сертифіката — для HTTPS потрібен реальний домен і, наприклад,
     certbot, що поза межами цього навчального проєкту). Якщо у вас є
     домен і TLS-термінація — увімкніть `DJANGO_SECURE_SSL_REDIRECT` та
     інші прапорці з `.env.example`.

2. Запустіть:

   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```

   При старті `web`-контейнер сам застосує міграції та збере статику
   (`docker/entrypoint.prod.sh`) — окремо викликати `migrate`/`collectstatic`
   не потрібно.

3. Сайт буде доступний на <http://your-server-ip/> (порт 80). API — на
   тому ж хості під `/api/`, адмінка — під `/admin/`.

4. Створити суперкористувача в уже запущеному контейнері:

   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```
5. Завантажити тестові категорії (3 шт) та продукти (9 шт):

   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py loaddata initial_products
   ```

**Топологія мережі:** `db` і `web` не мають портів, прокинутих на хост —
єдина точка входу зовні — `nginx` на порту 80. Це навмисне обмеження
поверхні атаки, типове для продакшену.

## Приклади використання API (JWT)

Повна інтерактивна документація — `/api/docs/` (там же можна натиснути
**Authorize** і виконувати запити прямо з браузера). Нижче — швидкі
приклади через `curl`.

**1. Реєстрація:**

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "email": "ivan@example.com", "password": "StrongPass123!", "password2": "StrongPass123!"}'
```

**2. Логін — отримати access/refresh токени:**

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "password": "StrongPass123!"}'
# → {"access": "...", "refresh": "..."}
```

**3. Запит із access-токеном:**

```bash
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <access-токен>"
```

**4. Оновлення протухлого access-токена:**

```bash
curl -X POST http://localhost:8000/api/users/login/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh-токен>"}'
# → {"access": "новий-токен", "refresh": "новий-refresh (ротація увімкнена)"}
```

Access живе 15 хв, refresh — 7 днів і ротується при кожному оновленні.

**5. Гість і кошик (без JWT):** кошик ідентифікується заголовком
`X-Cart-Token`, який повертається в кожній відповіді `/api/cart/` у полі
`"token"`:

```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 2}'
# → {"token": "xxxxxxxx-xxxx-...", "items": [...], ...}

curl http://localhost:8000/api/cart/ -H "X-Cart-Token: xxxxxxxx-xxxx-..."
```

## Тести та лінтери

```bash
uv run pytest                                    # тести
uv run pytest --cov --cov-report=term-missing    # тести з покриттям (~97%)
uv run flake8 .                                  # лінтер стилю
uv run mypy .                                    # перевірка типізації
```

## Структура проєкту

```
myshop/
├── config/              # Django settings (base/dev/prod), urls, wsgi/asgi
├── common/              # Спільне: health-check, IsOwner, TimeStampedModel
├── products/            # Каталог: Category, Product, фільтри, admin
├── cart/                # Кошик (гостьовий токен + user), API
├── orders/              # Замовлення, чекаут, аналітика в адмінці
├── users/               # Реєстрація, JWT, профіль
├── reviews/             # Відгуки з перевіркою покупки
├── templates/admin/     # Кастомні шаблони адмінки (сторінка аналітики)
├── frontend/            # React SPA (Vite): каталог, кошик, чекаут, кабінет
├── nginx/               # Dockerfile (збірка React) + nginx.conf для prod
├── docker/              # entrypoint.prod.sh (migrate → collectstatic → gunicorn)
├── .github/workflows/   # CI: flake8, mypy, pytest --cov
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── Dockerfile           # Образ Django-застосунку (спільний для dev/prod)
├── pyproject.toml       # Залежності бекенду (uv)
└── manage.py
```

Кожен Django-застосунок має власні `models.py`, `serializers.py`,
`views.py`, `admin.py`, `urls.py` і `tests/` — типова модульна структура
DRF-проєкту з розподілом відповідальності за доменом.

## Чек-ліст перед здачею

- [x] Проєкт запускається командою `docker compose -f docker-compose.dev.yml up --build` (dev) і `docker compose -f docker-compose.prod.yml up --build` (prod) на чистій системі
- [x] Використовується PostgreSQL
- [x] Каталог: реалізовано фільтри, пошук, пагінацію
- [x] Сторінка товару: є деталі, відгуки, кнопка додавання в кошик
- [x] Кошик: можна керувати вмістом, розраховується сума, є перевірка залишків
- [x] Оформлення замовлення: створюється замовлення, надсилається email, є валідація
- [x] Особистий кабінет: працює реєстрація, вхід, історія замовлень, редагування профілю
- [x] REST API: працює авторизація через JWT, є документація, налаштовані права доступу
- [x] Адмін-панель: є аналітика, фільтри, зручне керування даними
- [x] Swagger/OpenAPI документація доступна і працює коректно
- [x] Код містить типізацію та докстрінги
- [x] Лінтери (flake8/mypy) проходять без критичних помилок
- [x] Базові тести реалізовані та проходять успішно (59 тестів, ~97% покриття)
- [x] README є повним та зрозумілим
- [x] Коміти змістовні, гілки використовуються правильно 
- [x] Цей чек-ліст доданий до проєкту

## Статус реалізації по етапах

- [x] Етап 1 — Скелет проєкту, Docker (dev), налаштування dev/prod, CI
- [x] Етап 2 — Моделі даних (Category, Product, Cart/CartItem, Order/OrderItem, Review, Profile)
- [x] Етап 3 — REST API каталогу: фільтри, пошук, сортування, тести
- [x] Етап 4 — Відгуки з перевіркою покупки, тести
- [x] Етап 5 — API кошика: гостьовий токен, злиття при логіні, перевірка залишків, тести
- [x] Етап 6 — API користувачів: реєстрація, JWT логін/refresh, профіль, зміна пароля, тести
- [x] Етап 7 — API замовлень: оформлення з кошика, списання/повернення складу, email, скасування, тести
- [x] Етап 8 — Права доступу (IsOwner) та документація API (drf-spectacular)
- [x] Етап 9 — Адмін-панель: аналітика, фільтри, масові дії
- [x] Етап 10 — Скелет React: роутинг, JWT auto-refresh, layout, логін/реєстрація
- [x] Етап 11 — React: каталог і сторінка товару
- [x] Етап 12 — React: кошик, чекаут, особистий кабінет, історія замовлень
- [x] Етап 13 — Якість коду: типізація, лінтери, розширене покриття тестами (~97%)
- [x] Етап 14 — Продакшн-інфраструктура (Docker prod, nginx, збірка React), фінальний README
- [ ] Етап 15 (бонус) — GraphQL-аналітика

## Відомі обмеження й можливі покращення

- **HTTPS не налаштований** — продакшн-стек обслуговує звичайний HTTP;
  для реального деплою потрібен домен і TLS (наприклад, через
  certbot/nginx або хмарний балансувальник із HTTPS).
- **Гостьовий чекаут відсутній** — оформити замовлення може лише
  зареєстрований користувач (свідоме архітектурне рішення, узгоджене на
  Етапі 7).
- **GraphQL-аналітика** — бонусне завдання з ТЗ, не реалізоване;
  замість цього зроблено розширене покриття тестами (~97%) і CI з
  автоматичним звітом покриття, що теж у списку рекомендованих бонусів.
