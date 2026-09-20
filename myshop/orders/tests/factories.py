"""Фабрики тестових замовлень."""
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from orders.models import Order, OrderItem
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    status = Order.Status.DELIVERED
    total_price = Decimal("0.00")
    shipping_address = "м. Одеса, вул. Тестова, 1"


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    product_name = factory.LazyAttribute(lambda obj: obj.product.name)
    quantity = 1
    price = factory.LazyAttribute(lambda obj: obj.product.price)
