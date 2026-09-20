"""Тести API замовлень: /api/orders/."""
from decimal import Decimal

import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cart.tests.factories import CartItemFactory
from orders.models import Order
from orders.tests.factories import OrderFactory
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

ORDERS_URL = reverse("order-list")


def order_detail_url(order_id: int) -> str:
    return reverse("order-detail", kwargs={"pk": order_id})


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_order_requires_authentication(api_client: APIClient) -> None:
    response = api_client.get(ORDERS_URL)

    assert response.status_code in {
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    }


def test_create_order_from_cart_success(api_client: APIClient) -> None:
    user = UserFactory()
    product = ProductFactory(stock=10, price=Decimal("100.00"))
    cart_item = CartItemFactory(cart__user=user, product=product, quantity=3)
    api_client.force_authenticate(user)

    response = api_client.post(
        ORDERS_URL, {"shipping_address": "м. Одеса, вул. Тестова, 1"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["total_price"] == "300.00"
    product.refresh_from_db()
    assert product.stock == 7
    assert not cart_item.cart.items.exists()


def test_create_order_with_empty_cart_fails(api_client: APIClient) -> None:
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.post(ORDERS_URL, {"shipping_address": "Адреса"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Order.objects.filter(user=user).exists()


def test_create_order_insufficient_stock_fails(api_client: APIClient) -> None:
    user = UserFactory()
    product = ProductFactory(stock=2)
    CartItemFactory(cart__user=user, product=product, quantity=5)
    api_client.force_authenticate(user)

    response = api_client.post(ORDERS_URL, {"shipping_address": "Адреса"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    product.refresh_from_db()
    assert product.stock == 2
    assert not Order.objects.filter(user=user).exists()


def test_order_creation_sends_email_to_buyer(api_client: APIClient) -> None:
    user = UserFactory(email="buyer@example.com")
    product = ProductFactory(stock=5)
    CartItemFactory(cart__user=user, product=product, quantity=1)
    api_client.force_authenticate(user)

    api_client.post(ORDERS_URL, {"shipping_address": "Адреса"})

    assert any("buyer@example.com" in message.to for message in mail.outbox)


def test_list_orders_returns_only_own(api_client: APIClient) -> None:
    user_a = UserFactory()
    user_b = UserFactory()
    OrderFactory(user=user_a)
    OrderFactory(user=user_b)
    api_client.force_authenticate(user_a)

    response = api_client.get(ORDERS_URL)

    assert response.data["count"] == 1


def test_retrieve_other_users_order_returns_404(api_client: APIClient) -> None:
    owner = UserFactory()
    other = UserFactory()
    order = OrderFactory(user=owner)
    api_client.force_authenticate(other)

    response = api_client.get(order_detail_url(order.id))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cancel_pending_order_via_delete(api_client: APIClient) -> None:
    user = UserFactory()
    order = OrderFactory(user=user, status=Order.Status.PENDING)
    api_client.force_authenticate(user)

    response = api_client.delete(order_detail_url(order.id))

    assert response.status_code == status.HTTP_200_OK
    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED


def test_cancel_shipped_order_forbidden(api_client: APIClient) -> None:
    user = UserFactory()
    order = OrderFactory(user=user, status=Order.Status.SHIPPED)
    api_client.force_authenticate(user)

    response = api_client.delete(order_detail_url(order.id))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    order.refresh_from_db()
    assert order.status == Order.Status.SHIPPED


def test_patch_status_to_cancelled_succeeds(api_client: APIClient) -> None:
    user = UserFactory()
    order = OrderFactory(user=user, status=Order.Status.PENDING)
    api_client.force_authenticate(user)

    response = api_client.patch(order_detail_url(order.id), {"status": "cancelled"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "cancelled"


def test_patch_status_to_other_value_forbidden(api_client: APIClient) -> None:
    user = UserFactory()
    order = OrderFactory(user=user, status=Order.Status.PENDING)
    api_client.force_authenticate(user)

    response = api_client.patch(order_detail_url(order.id), {"status": "delivered"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    order.refresh_from_db()
    assert order.status == Order.Status.PENDING
