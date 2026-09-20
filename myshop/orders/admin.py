"""Django Admin для замовлень: фільтри, масові дії, дашборд аналітики."""
from django.contrib import admin
from django.db.models import Avg, Count, F, QuerySet, Sum
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import URLPattern, path, reverse

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Позиції замовлення показуються лише для перегляду — редагувати заднім
    числом ціну/кількість купленого не можна, це історичний запис."""

    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "quantity", "price"]
    can_delete = False

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Керування замовленнями + окрема сторінка аналітики (кнопка вгорі списку)."""

    list_display = ["id", "user", "status", "payment_method", "total_price", "created_at"]
    list_filter = ["status", "payment_method"]
    search_fields = ["id", "user__username", "user__email"]
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    actions = [
        "mark_as_paid",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
    ]

    REVENUE_STATUSES = [Order.Status.PAID, Order.Status.SHIPPED, Order.Status.DELIVERED]

    def get_urls(self) -> list[URLPattern]:
        custom_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="orders_order_analytics",
            ),
        ]
        return custom_urls + super().get_urls()

    def changelist_view(self, request: HttpRequest, extra_context=None) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["analytics_url"] = reverse("admin:orders_order_analytics")
        return super().changelist_view(request, extra_context=extra_context)

    def analytics_view(self, request: HttpRequest) -> TemplateResponse:
        """Аналітична панель: виторг, середній чек, топ-товари, статуси.

        "Виторг" рахується лише по замовленнях у статусах paid/shipped/
        delivered — pending ще не оплачено, cancelled не рахується.
        """
        paid_orders = Order.objects.filter(status__in=self.REVENUE_STATUSES)

        totals = paid_orders.aggregate(
            total_revenue=Sum("total_price"),
            average_order_value=Avg("total_price"),
            paid_orders_count=Count("id"),
        )

        status_labels = dict(Order.Status.choices)
        orders_by_status = list(
            Order.objects.values("status").annotate(count=Count("id")).order_by("status")
        )
        for row in orders_by_status:
            row["label"] = status_labels.get(row["status"], row["status"])

        top_products = (
            OrderItem.objects.filter(order__status__in=self.REVENUE_STATUSES)
            .values("product_name")
            .annotate(
                total_quantity=Sum("quantity"),
                total_revenue=Sum(F("price") * F("quantity")),
            )
            .order_by("-total_quantity")[:5]
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Аналітика замовлень",
            "total_revenue": totals["total_revenue"] or 0,
            "average_order_value": totals["average_order_value"] or 0,
            "paid_orders_count": totals["paid_orders_count"] or 0,
            "orders_by_status": orders_by_status,
            "top_products": top_products,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/orders/analytics.html", context)

    @admin.action(description="Позначити як оплачені")
    def mark_as_paid(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.exclude(status=Order.Status.CANCELLED).update(
            status=Order.Status.PAID
        )
        self.message_user(request, f"Оновлено замовлень: {updated}.")

    @admin.action(description="Позначити як відправлені")
    def mark_as_shipped(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.exclude(status=Order.Status.CANCELLED).update(
            status=Order.Status.SHIPPED
        )
        self.message_user(request, f"Оновлено замовлень: {updated}.")

    @admin.action(description="Позначити як доставлені")
    def mark_as_delivered(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.exclude(status=Order.Status.CANCELLED).update(
            status=Order.Status.DELIVERED
        )
        self.message_user(request, f"Оновлено замовлень: {updated}.")

    @admin.action(description="Скасувати вибрані замовлення")
    def mark_as_cancelled(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.exclude(status=Order.Status.DELIVERED).update(
            status=Order.Status.CANCELLED
        )
        self.message_user(request, f"Скасовано замовлень: {updated}.")
