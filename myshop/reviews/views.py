"""API-view відгуків на товар."""
from typing import cast

from django.contrib.auth.models import User as AuthUser
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, serializers
from rest_framework.serializers import BaseSerializer

from orders.models import Order, OrderItem
from products.models import Product
from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ProductReviewListCreateView(generics.ListCreateAPIView):
    """GET — список відгуків товару (публічно, без авторизації).

    POST — залишити відгук. Дозволено лише авторизованим користувачам,
    які фактично купили цей товар (мають OrderItem з ним у не скасованому
    замовленні), і лише один відгук на товар від одного користувача.
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_product(self) -> Product:
        return get_object_or_404(
            Product, pk=self.kwargs["product_id"], is_active=True
        )

    def get_queryset(self) -> QuerySet[Review]:
        return (
            Review.objects.filter(  # type: ignore[attr-defined]
                product_id=self.kwargs["product_id"]
            ).select_related("user")
        )

    def perform_create(self, serializer: BaseSerializer) -> None:
        # Сигнатура супертипу (CreateModelMixin) очікує BaseSerializer;
        # тут це завжди ReviewSerializer (єдиний serializer_class цього
        # view), тому звужуємо тип явним cast для доступу до .save(...).
        product = self.get_product()
        # permission_classes = [IsAuthenticatedOrReadOnly] гарантує в
        # рантаймі, що для POST request.user — не AnonymousUser.
        user = cast(AuthUser, self.request.user)

        has_purchased = (
            OrderItem.objects.filter(product=product, order__user=user)
            .exclude(order__status=Order.Status.CANCELLED)
            .exists()
        )
        if not has_purchased:
            raise serializers.ValidationError(
                {"detail": "Залишити відгук можна лише після покупки цього товару."}
            )

        if Review.objects.filter(  # type: ignore[attr-defined]
            product=product, user=user
        ).exists():
            raise serializers.ValidationError(
                {"detail": "Ви вже залишили відгук на цей товар."}
            )

        serializer.save(user=user, product=product)
