"""Django Admin для користувачів: Profile вбудовано прямо в сторінку User,
а не винесено окремим пунктом меню — це зручніше для одного адміна."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Профіль (телефон, адреса доставки)"


class CustomUserAdmin(UserAdmin):
    """Стандартна адмінка User (пароль, права, групи) + вкладений Profile."""

    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
