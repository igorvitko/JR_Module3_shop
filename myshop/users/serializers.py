"""Серіалізатори реєстрації, профілю та зміни пароля."""
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import Profile

# User — рантайм-значення get_user_model(), використовується як Meta.model
# і для .objects.create_user(). Для анотацій типів використовуємо
# AbstractBaseUser: mypy не дозволяє брати динамічну змінну як тип
# (django-stubs спеціально не робить User валідним типом сам по собі).
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Реєстрація нового користувача.

    Profile створюється автоматично сигналом post_save (users/signals.py)
    одразу після User.objects.create_user, тут його чіпати не треба.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Підтвердження пароля")

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Паролі не збігаються."})
        return attrs

    def create(self, validated_data: dict) -> AbstractBaseUser:
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    """Базові редаговані поля User, вкладені в профіль."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username"]


class ProfileSerializer(serializers.ModelSerializer):
    """Перегляд і редагування особистого кабінету."""

    user = UserSerializer(required=False)

    class Meta:
        model = Profile
        fields = ["user", "phone", "default_shipping_address"]

    def update(self, instance: Profile, validated_data: dict) -> Profile:
        user_data = validated_data.pop("user", None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Зміна пароля поточного користувача (потребує старий пароль)."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неправильний поточний пароль.")
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Паролі не збігаються."})
        return attrs

    def save(self, **kwargs) -> AbstractBaseUser:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
