"""API-view кошика: єдиний ендпоінт /api/cart/ для GET/POST/PATCH/DELETE."""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from cart.serializers import CartItemWriteSerializer, CartSerializer


class CartView(APIView):
    """Керування кошиком поточного користувача або гостя.

    Ідентифікація кошика:
    - авторизований користувач — кошик прив'язаний до user;
    - гість — кошик за токеном із заголовка ``X-Cart-Token``. Якщо токена
      немає або кошик з ним не знайдено, створюється новий кошик, і його
      токен повертається в тілі відповіді (поле "token"), щоб фронтенд
      зберіг його (наприклад, у localStorage) і надсилав далі з кожним
      запитом.

    Якщо авторизований користувач передає ``X-Cart-Token`` гостьового
    кошика (сценарій: додав товари до логіну, потім увійшов в акаунт),
    цей кошик автоматично зливається з кошиком користувача.
    """

    permission_classes = [AllowAny]

    def get_cart(self, request: Request) -> Cart:
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            self._merge_guest_cart_if_any(request, cart)
            return cart

        guest_cart = self._find_guest_cart(request)
        return guest_cart or Cart.objects.create()

    @staticmethod
    def _find_guest_cart(request: Request) -> Cart | None:
        token = request.headers.get("X-Cart-Token")
        if not token:
            return None
        try:
            return Cart.objects.filter(token=token, user__isnull=True).first()
        except (ValueError, DjangoValidationError):
            # Некоректний формат токена — трактуємо як "кошика немає".
            return None

    def _merge_guest_cart_if_any(self, request: Request, user_cart: Cart) -> None:
        guest_cart = self._find_guest_cart(request)
        if guest_cart is None or guest_cart.pk == user_cart.pk:
            return

        with transaction.atomic():
            for item in guest_cart.items.select_related("product"):
                existing = user_cart.items.filter(product=item.product).first()
                if existing:
                    existing.quantity = min(
                        existing.quantity + item.quantity, item.product.stock
                    )
                    existing.save(update_fields=["quantity"])
                else:
                    CartItem.objects.create(
                        cart=user_cart,
                        product=item.product,
                        quantity=min(item.quantity, item.product.stock),
                    )
            guest_cart.delete()

    def get(self, request: Request) -> Response:
        """Повертає поточний кошик з позиціями та підсумковою сумою."""
        cart = self.get_cart(request)
        return Response(CartSerializer(cart).data)

    @extend_schema(
        request=CartItemWriteSerializer,
        examples=[
            OpenApiExample(
                "Приклад запиту",
                value={"product": 1, "quantity": 2},
                request_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        """Додає товар у кошик; якщо він уже там — збільшує кількість."""
        cart = self.get_cart(request)
        serializer = CartItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        existing_item = cart.items.filter(product=product).first()
        current_quantity = existing_item.quantity if existing_item else 0
        new_quantity = current_quantity + quantity

        if new_quantity > product.stock:
            return Response(
                {"detail": f"На складі доступно лише {product.stock} од. товару."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if existing_item:
            existing_item.quantity = new_quantity
            existing_item.save(update_fields=["quantity"])
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=new_quantity)

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def patch(self, request: Request) -> Response:
        """Встановлює точну кількість товару в кошику (не додає, а замінює)."""
        cart = self.get_cart(request)
        serializer = CartItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        item = cart.items.filter(product=product).first()
        if item is None:
            return Response(
                {"detail": "Цього товару немає в кошику."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if quantity > product.stock:
            return Response(
                {"detail": f"На складі доступно лише {product.stock} од. товару."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.quantity = quantity
        item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data)

    def delete(self, request: Request) -> Response:
        """Видаляє одну позицію (?product=<id>) або очищає весь кошик."""
        cart = self.get_cart(request)
        product_id = request.query_params.get("product")

        if product_id:
            deleted_count, _ = cart.items.filter(product_id=product_id).delete()
            if not deleted_count:
                return Response(
                    {"detail": "Цього товару немає в кошику."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            cart.items.all().delete()

        return Response(CartSerializer(cart).data)
