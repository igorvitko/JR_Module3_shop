"""Серіалізатор відгуків."""
from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Відгук на товар.

    Поле product навмисно відсутнє тут: воно береться з URL
    (/api/products/<product_id>/reviews/) і підставляється у
    ProductReviewListCreateView.perform_create, а не приходить у тілі
    запиту — так неможливо залишити відгук "не на той" товар.
    """

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
