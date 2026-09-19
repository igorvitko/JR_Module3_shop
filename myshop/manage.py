#!/usr/bin/env python
"""Утиліта командного рядка Django для адміністративних задач."""
import os
import sys


def main() -> None:
    """Точка входу для запуску адміністративних команд Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не вдалося імпортувати Django. Переконайтесь, що він встановлений "
            "та доступний у змінній оточення PYTHONPATH. Ви точно активували "
            "віртуальне середовище (uv sync / .venv)?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
