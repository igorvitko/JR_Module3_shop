"""API-view реєстрації, профілю та зміни пароля.

Логін і оновлення JWT-токенів реалізовані стандартними view з
rest_framework_simplejwt (TokenObtainPairView / TokenRefreshView) —
див. users/urls.py, тут власного коду для них не потрібно.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response

from users.models import Profile
from users.serializers import (
    ChangePasswordSerializer,
    ProfileSerializer,
    RegisterSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Реєстрація нового користувача. Доступно без авторизації."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """Перегляд і редагування профілю поточного користувача (Особистий кабінет)."""

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Profile:
        return self.request.user.profile


class ChangePasswordView(generics.GenericAPIView):
    """Зміна пароля поточного користувача."""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Пароль успішно змінено."})
