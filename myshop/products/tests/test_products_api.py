"""Тести REST API каталогу товарів (/api/products/, /api/categories/)."""
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from products.tests.factories import CategoryFactory, ProductFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_product_list_returns_only_active_products(api_client: APIClient) -> None:
    """Неактивні товари не повинні потрапляти у публічний каталог."""
    ProductFactory(is_active=True)
    ProductFactory(is_active=False)

    response = api_client.get(reverse("product-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


def test_product_list_filters_by_category(api_client: APIClient) -> None:
    category_a = CategoryFactory()
    category_b = CategoryFactory()
    ProductFactory(category=category_a)
    ProductFactory(category=category_b)

    response = api_client.get(reverse("product-list"), {"category": category_a.id})

    assert response.data["count"] == 1
    assert response.data["results"][0]["category"] == category_a.id


def test_product_list_filters_by_price_range(api_client: APIClient) -> None:
    ProductFactory(price=Decimal("50.00"))
    cheap_in_range = ProductFactory(price=Decimal("500.00"))

    response = api_client.get(
        reverse("product-list"), {"min_price": 100, "max_price": 1000}
    )

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == cheap_in_range.id


def test_product_list_search_by_name(api_client: APIClient) -> None:
    ProductFactory(name="Синя футболка")
    ProductFactory(name="Червоні джинси")

    response = api_client.get(reverse("product-list"), {"search": "футболка"})

    assert response.data["count"] == 1


def test_product_list_ordering_by_price(api_client: APIClient) -> None:
    ProductFactory(price=Decimal("300.00"))
    ProductFactory(price=Decimal("100.00"))

    response = api_client.get(reverse("product-list"), {"ordering": "price"})

    prices = [Decimal(item["price"]) for item in response.data["results"]]
    assert prices == sorted(prices)


def test_product_detail_returns_full_data(api_client: APIClient) -> None:
    product = ProductFactory()

    response = api_client.get(reverse("product-detail", kwargs={"pk": product.pk}))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == product.id
    assert "description" in response.data
    assert response.data["category"]["id"] == product.category_id


def test_product_detail_404_for_inactive_product(api_client: APIClient) -> None:
    product = ProductFactory(is_active=False)

    response = api_client.get(reverse("product-detail", kwargs={"pk": product.pk}))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_category_list(api_client: APIClient) -> None:
    CategoryFactory.create_batch(3)

    response = api_client.get(reverse("category-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
