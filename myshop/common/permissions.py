"""Спільні класи прав доступу, що використовуються в кількох застосунках."""
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwner(BasePermission):
    """Дозволяє дію лише власнику об'єкта (obj.user == request.user).

    Це object-level перевірка "про запас": основний захист — фільтрація
    в get_queryset() (наприклад, OrderViewSet.get_queryset повертає лише
    Order.objects.filter(user=request.user)), через що звернення до
    чужого id вже дає 404 ще до виклику has_object_permission. Але якщо
    хтось у майбутньому додасть view/дію, яка бере obj через
    Model.objects.get() напряму, минаючи get_queryset(), ця перевірка
    все одно не дасть віддати чи змінити чужі дані.
    """

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        return getattr(obj, "user_id", None) == request.user.id
