"""Реєстрація моделей cart в Django Admin."""
from django.contrib import admin

from cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "total_items", "created_at")
    inlines = [CartItemInline]
