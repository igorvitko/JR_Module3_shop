# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Системні залежності: libpq для psycopg, gcc для збірки колес за потреби.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# uv встановлюється копіюванням офіційного бінарника (без мережевого pip install).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Спершу лише файли залежностей — для кешування шару Docker.
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Тепер копіюємо решту коду проєкту.
COPY . .

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

# У dev команда перевизначається в docker-compose.dev.yml (runserver + автоперезавантаження).
# У prod (Етап 14) тут буде gunicorn.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
