"""Django Admin для товарів і категорій: фільтри, масові дії, швидке редагування."""
from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from products.models import Category, Product


class LowStockFilter(admin.SimpleListFilter):
    """Кастомний фільтр: товари, яких залишилось мало або немає взагалі."""

    title = "залишок на складі"
    parameter_name = "stock_level"

    def lookups(self, request: HttpRequest, model_admin) -> list[tuple[str, str]]:
        return [("low", "Мало (< 5 од.)"), ("out", "Немає в наявності")]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() == "low":
            return queryset.filter(stock__gt=0, stock__lt=5)
        if self.value() == "out":
            return queryset.filter(stock=0)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "product_count"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        # annotate замість N окремих product.objects.filter(category=...).count()
        # на кожен рядок списку — один запит замість N+1.
        return super().get_queryset(request).annotate(_product_count=Count("products"))

    @admin.display(description="К-сть товарів", ordering="_product_count")
    def product_count(self, obj: Category) -> int:
        # _product_count додається динамічно через .annotate() у
        # get_queryset() вище — mypy не бачить анотацій queryset, тому
        # це очікуване й безпечне придушення попередження нижче.
        return obj._product_count  # type: ignore[attr-defined]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "is_active"]
    list_display_links = ["name"]
    list_editable = ["price", "stock", "is_active"]
    list_filter = ["category", "is_active", LowStockFilter]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    actions = ["activate_products", "deactivate_products"]

    @admin.action(description="Активувати вибрані товари")
    def activate_products(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано товарів: {updated}.")

    @admin.action(description="Деактивувати вибрані товари")
    def deactivate_products(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано товарів: {updated}.")
