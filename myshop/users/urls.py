"""URL-маршрути користувачів: реєстрація, JWT-логін, профіль, пароль."""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import ChangePasswordView, ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", TokenObtainPairView.as_view(), name="user-login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="user-login-refresh"),
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="user-change-password"),
]
