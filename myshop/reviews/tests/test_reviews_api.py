"""Тести API відгуків: /api/products/<id>/reviews/."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from orders.models import Order
from orders.tests.factories import OrderItemFactory
from products.tests.factories import ProductFactory
from reviews.models import Review
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def reviews_url(product_id: int) -> str:
    return reverse("product-reviews", kwargs={"product_id": product_id})


def test_anyone_can_list_reviews(api_client: APIClient) -> None:
    product = ProductFactory()

    response = api_client.get(reviews_url(product.id))

    assert response.status_code == status.HTTP_200_OK


def test_anonymous_cannot_create_review(api_client: APIClient) -> None:
    product = ProductFactory()

    response = api_client.post(reviews_url(product.id), {"rating": 5, "comment": "Супер"})

    assert response.status_code in {
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    }


def test_user_without_purchase_cannot_review(api_client: APIClient) -> None:
    product = ProductFactory()
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.post(reviews_url(product.id), {"rating": 5, "comment": "Супер"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Review.objects.filter(product=product, user=user).exists()


def test_user_who_purchased_can_review(api_client: APIClient) -> None:
    product = ProductFactory()
    order_item = OrderItemFactory(product=product)
    user = order_item.order.user
    api_client.force_authenticate(user)

    response = api_client.post(reviews_url(product.id), {"rating": 4, "comment": "Добре"})

    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.filter(product=product, user=user, rating=4).exists()


def test_cannot_review_same_product_twice(api_client: APIClient) -> None:
    product = ProductFactory()
    order_item = OrderItemFactory(product=product)
    user = order_item.order.user
    api_client.force_authenticate(user)

    api_client.post(reviews_url(product.id), {"rating": 5, "comment": "Перший"})
    response = api_client.post(reviews_url(product.id), {"rating": 3, "comment": "Другий"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Review.objects.filter(product=product, user=user).count() == 1


def test_purchase_from_cancelled_order_does_not_count(api_client: APIClient) -> None:
    product = ProductFactory()
    order_item = OrderItemFactory(product=product, order__status=Order.Status.CANCELLED)
    user = order_item.order.user
    api_client.force_authenticate(user)

    response = api_client.post(reviews_url(product.id), {"rating": 5, "comment": "Супер"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Review.objects.filter(product=product, user=user).exists()
