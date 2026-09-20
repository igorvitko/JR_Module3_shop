"""URL-маршрути відгуків (вкладені під конкретний товар)."""
from django.urls import path

from reviews.views import ProductReviewListCreateView

urlpatterns = [
    path("reviews/", ProductReviewListCreateView.as_view(), name="product-reviews"),
]
