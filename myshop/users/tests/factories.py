"""Фабрика тестового користувача."""
import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Хешує пароль і явно зберігає користувача (заміна автозбереження,
        яке factory-boy прибирає в наступному мажорному релізі)."""
        obj.set_password(extracted or "TestPass123!")
        if create:
            obj.save()
