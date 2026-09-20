"""Перевірка, що OpenAPI-схема та Swagger UI генеруються без помилок.

Це важливо саме після додавання кастомних @extend_schema/OpenApiExample —
одна помилка в них ламає всю схему, і краще дізнатися про це з тесту,
а не при відкритті /api/docs/ вручну.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_openapi_schema_generates_without_errors() -> None:
    client = APIClient()

    response = client.get(reverse("schema"))

    assert response.status_code == 200


def test_swagger_ui_page_loads() -> None:
    client = APIClient()

    response = client.get(reverse("swagger-ui"))

    assert response.status_code == 200


def test_health_check_endpoint() -> None:
    client = APIClient()

    response = client.get(reverse("health-check"))

    assert response.status_code == 200
    assert response.data["status"] == "ok"
