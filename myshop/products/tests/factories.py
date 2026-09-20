"""Фабрики тестових даних для products (factory-boy).

Використовуються і в тестах інших застосунків (cart, orders, reviews),
які потребують готового товару/категорії — уникаємо дублювання коду.
"""
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from products.models import Category, Product


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Категорія {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Товар {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    description = "Опис товару для тестів."
    price = factory.Sequence(lambda n: Decimal(f"{100 + n}.00"))
    category = factory.SubFactory(CategoryFactory)
    is_active = True
    stock = 10
