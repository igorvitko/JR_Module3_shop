"""Тести API кошика: /api/cart/."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cart.models import Cart
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

CART_URL = reverse("cart")


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_guest_can_add_item_and_receives_token(api_client: APIClient) -> None:
    product = ProductFactory(stock=10)

    response = api_client.post(CART_URL, {"product": product.id, "quantity": 2})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["token"]
    assert response.data["total_items"] == 2
    assert response.data["items"][0]["product"]["id"] == product.id


def test_guest_cart_persists_across_requests_with_token(api_client: APIClient) -> None:
    product = ProductFactory(stock=10)
    create_response = api_client.post(CART_URL, {"product": product.id, "quantity": 1})
    token = create_response.data["token"]

    response = api_client.get(CART_URL, HTTP_X_CART_TOKEN=token)

    assert response.data["token"] == token
    assert response.data["total_items"] == 1


def test_adding_more_than_stock_fails(api_client: APIClient) -> None:
    product = ProductFactory(stock=3)

    response = api_client.post(CART_URL, {"product": product.id, "quantity": 5})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Cart.objects.filter(items__product=product).exists()


def test_adding_same_product_twice_accumulates_quantity(api_client: APIClient) -> None:
    product = ProductFactory(stock=10)
    create_response = api_client.post(CART_URL, {"product": product.id, "quantity": 2})
    token = create_response.data["token"]

    response = api_client.post(
        CART_URL, {"product": product.id, "quantity": 3}, HTTP_X_CART_TOKEN=token
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["total_items"] == 5


def test_patch_sets_exact_quantity(api_client: APIClient) -> None:
    product = ProductFactory(stock=10)
    create_response = api_client.post(CART_URL, {"product": product.id, "quantity": 2})
    token = create_response.data["token"]

    response = api_client.patch(
        CART_URL, {"product": product.id, "quantity": 7}, HTTP_X_CART_TOKEN=token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_items"] == 7


def test_patch_over_stock_fails(api_client: APIClient) -> None:
    product = ProductFactory(stock=5)
    create_response = api_client.post(CART_URL, {"product": product.id, "quantity": 2})
    token = create_response.data["token"]

    response = api_client.patch(
        CART_URL, {"product": product.id, "quantity": 99}, HTTP_X_CART_TOKEN=token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_specific_item_removes_it(api_client: APIClient) -> None:
    product_a = ProductFactory(stock=10)
    product_b = ProductFactory(stock=10)
    create_response = api_client.post(CART_URL, {"product": product_a.id, "quantity": 1})
    token = create_response.data["token"]
    api_client.post(CART_URL, {"product": product_b.id, "quantity": 1}, HTTP_X_CART_TOKEN=token)

    response = api_client.delete(
        f"{CART_URL}?product={product_a.id}", HTTP_X_CART_TOKEN=token
    )

    assert response.status_code == status.HTTP_200_OK
    remaining_ids = [item["product"]["id"] for item in response.data["items"]]
    assert remaining_ids == [product_b.id]


def test_delete_without_product_clears_whole_cart(api_client: APIClient) -> None:
    product = ProductFactory(stock=10)
    create_response = api_client.post(CART_URL, {"product": product.id, "quantity": 1})
    token = create_response.data["token"]

    response = api_client.delete(CART_URL, HTTP_X_CART_TOKEN=token)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == []


def test_authenticated_user_cart_persists_without_token(api_client: APIClient) -> None:
    user = UserFactory()
    product = ProductFactory(stock=10)
    api_client.force_authenticate(user)

    api_client.post(CART_URL, {"product": product.id, "quantity": 2})
    response = api_client.get(CART_URL)

    assert response.data["total_items"] == 2
    assert Cart.objects.filter(user=user).count() == 1


def test_guest_cart_merges_into_user_cart_on_login(api_client: APIClient) -> None:
    product = ProductFactory(stock=10)
    guest_response = api_client.post(CART_URL, {"product": product.id, "quantity": 2})
    guest_token = guest_response.data["token"]

    user = UserFactory()
    api_client.force_authenticate(user)
    response = api_client.get(CART_URL, HTTP_X_CART_TOKEN=guest_token)

    assert response.data["total_items"] == 2
    assert Cart.objects.filter(user=user).count() == 1
    assert not Cart.objects.filter(token=guest_token).exists()


def test_malformed_cart_token_header_does_not_crash(api_client: APIClient) -> None:
    """Довільний, не-UUID заголовок X-Cart-Token не повинен валити запит —
    очікувана поведінка: трактувати його як "кошика немає" і створити новий."""
    response = api_client.get(CART_URL, HTTP_X_CART_TOKEN="not-a-valid-uuid")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == []
    assert response.data["token"]
