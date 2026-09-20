"""API-view відгуків на товар."""
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, serializers

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

    def get_queryset(self):
        return (
            Review.objects.filter(product_id=self.kwargs["product_id"])
            .select_related("user")
        )

    def perform_create(self, serializer: ReviewSerializer) -> None:
        product = self.get_product()
        user = self.request.user

        has_purchased = (
            OrderItem.objects.filter(product=product, order__user=user)
            .exclude(order__status=Order.Status.CANCELLED)
            .exists()
        )
        if not has_purchased:
            raise serializers.ValidationError(
                {"detail": "Залишити відгук можна лише після покупки цього товару."}
            )

        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError(
                {"detail": "Ви вже залишили відгук на цей товар."}
            )

        serializer.save(user=user, product=product)
