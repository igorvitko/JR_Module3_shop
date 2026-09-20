"""Тести кастомної сторінки аналітики в Django Admin."""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from orders.models import Order
from orders.tests.factories import OrderFactory

pytestmark = pytest.mark.django_db

User = get_user_model()

ANALYTICS_URL_NAME = "admin:orders_order_analytics"


def test_analytics_page_requires_staff_login() -> None:
    client = Client()

    response = client.get(reverse(ANALYTICS_URL_NAME))

    # Django Admin редіректить неавторизованих на сторінку логіну.
    assert response.status_code == 302


def test_analytics_page_shows_correct_revenue_for_staff() -> None:
    staff = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="AdminPass123!"
    )
    OrderFactory(status=Order.Status.DELIVERED, total_price=Decimal("500.00"))
    OrderFactory(status=Order.Status.PAID, total_price=Decimal("200.00"))
    OrderFactory(status=Order.Status.PENDING, total_price=Decimal("100.00"))
    OrderFactory(status=Order.Status.CANCELLED, total_price=Decimal("999.00"))

    client = Client()
    client.force_login(staff)

    response = client.get(reverse(ANALYTICS_URL_NAME))

    assert response.status_code == 200
    # Рахуються лише paid/shipped/delivered — pending і cancelled ігноруються.
    assert response.context["total_revenue"] == Decimal("700.00")
    assert response.context["paid_orders_count"] == 2
