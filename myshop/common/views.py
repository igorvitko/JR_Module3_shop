"""Допоміжні view, що не належать конкретному домену застосунку."""
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request) -> Response:
    """Перевіряє, що застосунок запущений і має з'єднання з базою даних.

    Використовується для Docker healthcheck та ручної перевірки після
    деплою. Не потребує авторизації.
    """
    db_status = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception:  # noqa: BLE001 — навмисно широкий except для healthcheck
        db_status = "unavailable"

    return Response({"status": "ok", "database": db_status})
