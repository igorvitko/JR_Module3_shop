"""Тести API користувачів: реєстрація, JWT, профіль, зміна пароля."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

User = get_user_model()

REGISTER_URL = reverse("user-register")
LOGIN_URL = reverse("user-login")
REFRESH_URL = reverse("user-login-refresh")
PROFILE_URL = reverse("user-profile")
CHANGE_PASSWORD_URL = reverse("user-change-password")

VALID_PASSWORD = "StrongPass123!"


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


# --- Реєстрація ---


def test_register_creates_user_and_profile(api_client: APIClient) -> None:
    response = api_client.post(
        REGISTER_URL,
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": VALID_PASSWORD,
            "password2": VALID_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(username="newuser")
    assert hasattr(user, "profile")
    assert "password" not in response.data


def test_register_password_mismatch_fails(api_client: APIClient) -> None:
    response = api_client.post(
        REGISTER_URL,
        {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password": VALID_PASSWORD,
            "password2": "Different123!",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not User.objects.filter(username="newuser2").exists()


def test_register_weak_password_fails(api_client: APIClient) -> None:
    response = api_client.post(
        REGISTER_URL,
        {
            "username": "newuser3",
            "email": "newuser3@example.com",
            "password": "12345678",
            "password2": "12345678",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --- JWT логін / refresh ---


def test_login_returns_access_and_refresh_tokens(api_client: APIClient) -> None:
    user = UserFactory()

    response = api_client.post(
        LOGIN_URL, {"username": user.username, "password": "TestPass123!"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


def test_login_wrong_password_fails(api_client: APIClient) -> None:
    user = UserFactory()

    response = api_client.post(
        LOGIN_URL, {"username": user.username, "password": "WrongPassword!"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_returns_new_access_token(api_client: APIClient) -> None:
    user = UserFactory()
    login_response = api_client.post(
        LOGIN_URL, {"username": user.username, "password": "TestPass123!"}
    )
    refresh_token = login_response.data["refresh"]

    response = api_client.post(REFRESH_URL, {"refresh": refresh_token})

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


# --- Профіль ---


def test_profile_requires_authentication(api_client: APIClient) -> None:
    response = api_client.get(PROFILE_URL)

    assert response.status_code in {
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    }


def test_profile_get_returns_user_and_profile_data(api_client: APIClient) -> None:
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.get(PROFILE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"]["username"] == user.username


def test_profile_patch_updates_nested_and_own_fields(api_client: APIClient) -> None:
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.patch(
        PROFILE_URL,
        {"phone": "+380501112233", "user": {"first_name": "Ігор"}},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == "Ігор"
    assert user.profile.phone == "+380501112233"


# --- Зміна пароля ---


def test_change_password_success(api_client: APIClient) -> None:
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": "TestPass123!",
            "new_password": "NewStrongPass456!",
            "new_password2": "NewStrongPass456!",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NewStrongPass456!")


def test_change_password_wrong_old_password_fails(api_client: APIClient) -> None:
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": "WrongOldPassword!",
            "new_password": "NewStrongPass456!",
            "new_password2": "NewStrongPass456!",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_password_mismatch_fails(api_client: APIClient) -> None:
    user = UserFactory()
    api_client.force_authenticate(user)

    response = api_client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": "TestPass123!",
            "new_password": "NewStrongPass456!",
            "new_password2": "Mismatch789!",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
