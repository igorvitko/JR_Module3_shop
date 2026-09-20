"""URL-маршрути каталогу товарів."""
from rest_framework.routers import DefaultRouter

from products.views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
