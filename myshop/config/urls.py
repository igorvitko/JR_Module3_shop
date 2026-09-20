"""Кореневий urlconf проєкту myshop."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from common.views import health_check


@api_view(["GET"])
def api_root(request, format=None):  # noqa: A002 — "format" це стандартне ім'я DRF
    """Кореневий ендпоінт /api/ — ручний список основних ресурсів.

    Роутери застосунків навмисно на SimpleRouter (без автогенерованого
    "API root"), бо кілька DefaultRouter під одним префіксом /api/
    конфліктують за адресу "" — виграє лише перший підключений. Тут один
    список для всіх, зібраний вручну.
    """
    return Response(
        {
            "products": reverse("product-list", request=request, format=format),
            "categories": reverse("category-list", request=request, format=format),
            "cart": reverse("cart", request=request, format=format),
            "orders": reverse("order-list", request=request, format=format),
            "register": reverse("user-register", request=request, format=format),
            "login": reverse("user-login", request=request, format=format),
            "docs": reverse("swagger-ui", request=request, format=format),
        }
    )

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/health/", health_check, name="health-check"),
    # Swagger/OpenAPI документація REST API.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Ендпоінти застосунків додаються поетапно (Етапи 3–7):
    path("api/", include("products.urls")),  # /api/products/, /api/categories/
    path("api/products/<int:product_id>/", include("reviews.urls")),  # .../reviews/
    path("api/cart/", include("cart.urls")),
    path("api/", include("orders.urls")),  # /api/orders/
    path("api/users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
