"""Реєстрація моделей orders в Django Admin.

Аналітика (виторг, топ-товари тощо) додається на Етапі 9.
"""
from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    inlines = [OrderItemInline]
