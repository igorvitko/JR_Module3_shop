import { useState } from "react";
import { Link } from "react-router-dom";

import { removeFromCart, updateCartItem } from "../api/cart";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function CartPage() {
  const { cart, isLoading, refreshCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [pendingProductId, setPendingProductId] = useState(null);
  const [error, setError] = useState(null);

  async function handleQuantityChange(productId, quantity) {
    if (quantity < 1) return;
    setError(null);
    setPendingProductId(productId);
    try {
      await updateCartItem(productId, quantity);
      await refreshCart();
    } catch (err) {
      setError(err.response?.data?.detail ?? "Не вдалося оновити кількість.");
    } finally {
      setPendingProductId(null);
    }
  }

  async function handleRemove(productId) {
    setError(null);
    setPendingProductId(productId);
    try {
      await removeFromCart(productId);
      await refreshCart();
    } catch {
      setError("Не вдалося видалити товар.");
    } finally {
      setPendingProductId(null);
    }
  }

  if (isLoading) {
    return <p className="muted">Завантаження…</p>;
  }

  const items = cart?.items ?? [];

  return (
    <div className="cart-page">
      <h1>Кошик</h1>

      {error && <p className="form-error">{error}</p>}

      {items.length === 0 ? (
        <p className="muted">
          Кошик порожній. <Link to="/">Перейти до каталогу</Link>.
        </p>
      ) : (
        <>
          <ul className="cart-list">
            {items.map((item) => (
              <li key={item.id} className="cart-item">
                <div className="cart-item__image">
                  {item.product.image ? (
                    <img src={item.product.image} alt={item.product.name} />
                  ) : (
                    <div className="product-card__image-placeholder" aria-hidden="true" />
                  )}
                </div>

                <div className="cart-item__body">
                  <Link to={`/products/${item.product.id}`} className="cart-item__name">
                    {item.product.name}
                  </Link>
                  <p className="cart-item__price">{item.product.price} грн</p>
                </div>

                <div className="cart-item__quantity">
                  <button
                    type="button"
                    className="button"
                    disabled={pendingProductId === item.product.id || item.quantity <= 1}
                    onClick={() => handleQuantityChange(item.product.id, item.quantity - 1)}
                  >
                    −
                  </button>
                  <span>{item.quantity}</span>
                  <button
                    type="button"
                    className="button"
                    disabled={
                      pendingProductId === item.product.id ||
                      item.quantity >= item.product.stock
                    }
                    onClick={() => handleQuantityChange(item.product.id, item.quantity + 1)}
                  >
                    +
                  </button>
                </div>

                <p className="cart-item__subtotal">{item.subtotal} грн</p>

                <button
                  type="button"
                  className="link-button"
                  disabled={pendingProductId === item.product.id}
                  onClick={() => handleRemove(item.product.id)}
                >
                  Видалити
                </button>
              </li>
            ))}
          </ul>

          <div className="cart-summary">
            <p className="cart-summary__total">Разом: {cart.total_price} грн</p>
            {isAuthenticated ? (
              <Link to="/checkout" className="button button--accent">
                Оформити замовлення
              </Link>
            ) : (
              <Link to="/login" className="button button--accent">
                Увійти, щоб оформити замовлення
              </Link>
            )}
          </div>
        </>
      )}
    </div>
  );
}
