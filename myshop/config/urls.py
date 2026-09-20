"""Кореневий urlconf проєкту myshop."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from common.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
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
    # path("api/cart/", include("cart.urls")),
    # path("api/orders/", include("orders.urls")),
    # path("api/users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
