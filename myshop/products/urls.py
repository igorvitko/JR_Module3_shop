"""URL-маршрути каталогу товарів."""
from rest_framework.routers import SimpleRouter

from products.views import CategoryViewSet, ProductViewSet

# SimpleRouter (не DefaultRouter) — свідомо, щоб уникнути колізії кореневих
# "API root" сторінок, коли кілька роутерів підключені під одним префіксом
# /api/ (products.urls і orders.urls). Єдина коренева сторінка задана
# вручну в config/urls.py (api_root).
router = SimpleRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
