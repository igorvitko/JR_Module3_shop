"""Юніт-тести для common/permissions.py."""
import pytest
from django.test import RequestFactory

from common.permissions import IsOwner
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class _FakeOwnedObject:
    """Мінімальний об'єкт з user_id — щоб не тягнути реальну модель у юніт-тест."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id


def test_is_owner_allows_when_user_matches() -> None:
    user = UserFactory()
    request = RequestFactory().get("/")
    request.user = user
    permission = IsOwner()

    assert permission.has_object_permission(request, view=None, obj=_FakeOwnedObject(user.id))


def test_is_owner_denies_when_user_differs() -> None:
    owner = UserFactory()
    other = UserFactory()
    request = RequestFactory().get("/")
    request.user = other
    permission = IsOwner()

    assert not permission.has_object_permission(
        request, view=None, obj=_FakeOwnedObject(owner.id)
    )


def test_is_owner_denies_when_object_has_no_user_id() -> None:
    user = UserFactory()
    request = RequestFactory().get("/")
    request.user = user
    permission = IsOwner()

    assert not permission.has_object_permission(request, view=None, obj=object())
