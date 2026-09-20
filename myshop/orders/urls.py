"""URL-маршрути замовлень."""
from rest_framework.routers import SimpleRouter

from orders.views import OrderViewSet

# SimpleRouter — див. коментар у products/urls.py про колізію API root.
router = SimpleRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls
