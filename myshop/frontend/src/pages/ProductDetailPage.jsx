import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { addToCart } from "../api/cart";
import { fetchProduct, fetchReviews, submitReview } from "../api/products";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function ProductDetailPage() {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const { refreshCart } = useCart();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [quantity, setQuantity] = useState(1);
  const [addStatus, setAddStatus] = useState(null);

  const [reviewForm, setReviewForm] = useState({ rating: "5", comment: "" });
  const [reviewError, setReviewError] = useState(null);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    setAddStatus(null);

    Promise.all([fetchProduct(id), fetchReviews(id)])
      .then(([productData, reviewsData]) => {
        if (cancelled) return;
        setProduct(productData);
        setReviews(reviewsData.results);
        setQuantity(1);
      })
      .catch(() => {
        if (!cancelled) setError("Не вдалося завантажити товар.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [id]);

  async function handleAddToCart(event) {
    event.preventDefault();
    setAddStatus(null);
    try {
      await addToCart(product.id, quantity);
      await refreshCart();
      setAddStatus({ type: "success", message: "Додано в кошик." });
    } catch (err) {
      setAddStatus({
        type: "error",
        message: err.response?.data?.detail ?? "Не вдалося додати товар у кошик.",
      });
    }
  }

  async function handleSubmitReview(event) {
    event.preventDefault();
    setReviewError(null);
    setIsSubmittingReview(true);
    try {
      const newReview = await submitReview(product.id, {
        rating: Number(reviewForm.rating),
        comment: reviewForm.comment,
      });
      setReviews((prev) => [newReview, ...prev]);
      setReviewForm({ rating: "5", comment: "" });
    } catch (err) {
      setReviewError(err.response?.data?.detail ?? "Не вдалося залишити відгук.");
    } finally {
      setIsSubmittingReview(false);
    }
  }

  if (isLoading) {
    return <p className="muted">Завантаження…</p>;
  }
  if (error) {
    return <p className="form-error">{error}</p>;
  }
  if (!product) {
    return null;
  }

  return (
    <div className="product-detail">
      <div className="product-detail__main">
        <div className="product-detail__image">
          {product.image ? (
            <img src={product.image} alt={product.name} />
          ) : (
            <div className="product-card__image-placeholder" aria-hidden="true" />
          )}
        </div>

        <div className="product-detail__info">
          {product.category && (
            <p className="product-detail__category">{product.category.name}</p>
          )}
          <h1>{product.name}</h1>
          <p className="product-detail__price">{product.price} грн</p>
          {product.average_rating != null && (
            <p className="product-card__rating">★ {product.average_rating.toFixed(1)}</p>
          )}
          <p className="product-detail__description">{product.description}</p>

          {product.is_in_stock ? (
            <form className="add-to-cart-form" onSubmit={handleAddToCart}>
              <label className="field field--inline">
                <span>Кількість</span>
                <input
                  type="number"
                  min="1"
                  max={product.stock}
                  value={quantity}
                  onChange={(event) => setQuantity(Number(event.target.value))}
                />
              </label>
              <button type="submit" className="button button--accent">
                Додати в кошик
              </button>
            </form>
          ) : (
            <p className="product-card__out-of-stock">Немає в наявності</p>
          )}

          {addStatus && (
            <p className={addStatus.type === "error" ? "form-error" : "form-success"}>
              {addStatus.message}
            </p>
          )}
        </div>
      </div>

      <section className="reviews-section">
        <h2>Відгуки</h2>

        {isAuthenticated ? (
          <form className="review-form" onSubmit={handleSubmitReview}>
            <label className="field field--inline">
              <span>Оцінка</span>
              <select
                value={reviewForm.rating}
                onChange={(event) =>
                  setReviewForm((prev) => ({ ...prev, rating: event.target.value }))
                }
              >
                {[5, 4, 3, 2, 1].map((value) => (
                  <option key={value} value={value}>
                    {value} ★
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Коментар</span>
              <textarea
                rows={3}
                value={reviewForm.comment}
                onChange={(event) =>
                  setReviewForm((prev) => ({ ...prev, comment: event.target.value }))
                }
              />
            </label>
            {reviewError && <p className="form-error">{reviewError}</p>}
            <button type="submit" className="button" disabled={isSubmittingReview}>
              {isSubmittingReview ? "Надсилаємо…" : "Залишити відгук"}
            </button>
          </form>
        ) : (
          <p className="muted">
            Щоб залишити відгук, потрібно <Link to="/login">увійти</Link> і мати покупку цього
            товару.
          </p>
        )}

        {reviews.length === 0 ? (
          <p className="muted">Відгуків ще немає.</p>
        ) : (
          <ul className="review-list">
            {reviews.map((review) => (
              <li key={review.id} className="review-item">
                <div className="review-item__header">
                  <strong>{review.user}</strong>
                  <span>{"★".repeat(review.rating)}</span>
                </div>
                {review.comment && <p>{review.comment}</p>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
