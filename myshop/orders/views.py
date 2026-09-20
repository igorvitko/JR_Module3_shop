"""API-view замовлень: створення з кошика, перегляд історії, скасування."""
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderCreateSerializer, OrderSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Замовлення поточного користувача.

    - list/retrieve — лише свої замовлення (чужі повертають 404, а не 403,
      щоб не підтверджувати саме існування чужого замовлення);
    - create — оформлення з кошика (див. OrderCreateSerializer);
    - PATCH/PUT — дозволяють лише перевести статус у "cancelled";
    - DELETE — м'яке скасування (переводить у статус CANCELLED, запис
      із БД фізично не видаляється — потрібна історія замовлень).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderSerializer(order, context=self.get_serializer_context())
        return Response(output_serializer.data, status=201)

    def perform_update(self, serializer: OrderSerializer) -> None:
        # serializer.instance — саме той об'єкт, який далі серіалізується у
        # відповідь; якщо замість нього повторно зробити get_object(), у
        # відповіді залишаться старі (несинхронізовані) дані.
        order: Order = serializer.instance
        new_status = self.request.data.get("status")

        if new_status != Order.Status.CANCELLED:
            raise PermissionDenied("Через API можна лише скасувати замовлення.")
        if not order.can_be_cancelled:
            raise PermissionDenied("Це замовлення вже не можна скасувати.")

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

    def destroy(self, request, *args, **kwargs) -> Response:
        order = self.get_object()
        if not order.can_be_cancelled:
            raise PermissionDenied("Це замовлення вже не можна скасувати.")

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)
