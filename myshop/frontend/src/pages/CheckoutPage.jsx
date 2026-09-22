import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createOrder } from "../api/orders";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

const PAYMENT_METHODS = [
  { value: "card", label: "Оплата карткою (мок)" },
  { value: "cash_on_delivery", label: "Оплата при отриманні" },
];

export default function CheckoutPage() {
  const { cart, refreshCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ shipping_address: "", payment_method: "card" });
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const items = cart?.items ?? [];

  // Підставляємо адресу за замовчуванням з профілю, коли він завантажиться —
  // але лише якщо поле ще порожнє, щоб не затерти те, що людина вже сама
  // почала вводити.
  useEffect(() => {
    if (user?.default_shipping_address && !form.shipping_address) {
      setForm((prev) => ({ ...prev, shipping_address: user.default_shipping_address }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const order = await createOrder(form);
      await refreshCart();
      navigate("/orders", { replace: true, state: { justCreatedOrderId: order.id } });
    } catch (err) {
      const data = err.response?.data ?? {};
      setError(data.detail ?? data.shipping_address?.[0] ?? "Не вдалося оформити замовлення.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (items.length === 0) {
    return (
      <div className="checkout-page">
        <h1>Оформлення замовлення</h1>
        <p className="muted">Кошик порожній — оформити замовлення нема з чого.</p>
      </div>
    );
  }

  return (
    <div className="checkout-page">
      <h1>Оформлення замовлення</h1>

      <div className="checkout-layout">
        <form className="checkout-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Адреса доставки</span>
            <textarea
              name="shipping_address"
              rows={3}
              value={form.shipping_address}
              onChange={handleChange}
              required
            />
            {user?.default_shipping_address && (
              <small className="field-hint">
                Підставлено адресу за замовчуванням з вашого профілю — можна відредагувати.
              </small>
            )}
          </label>

          <label className="field">
            <span>Спосіб оплати</span>
            <select name="payment_method" value={form.payment_method} onChange={handleChange}>
              {PAYMENT_METHODS.map((method) => (
                <option key={method.value} value={method.value}>
                  {method.label}
                </option>
              ))}
            </select>
          </label>

          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="button button--accent" disabled={isSubmitting}>
            {isSubmitting ? "Оформлюємо…" : "Підтвердити замовлення"}
          </button>
        </form>

        <aside className="checkout-summary">
          <h2>Ваше замовлення</h2>
          <ul>
            {items.map((item) => (
              <li key={item.id}>
                {item.product.name} × {item.quantity} — {item.subtotal} грн
              </li>
            ))}
          </ul>
          <p className="cart-summary__total">Разом: {cart.total_price} грн</p>
        </aside>
      </div>
    </div>
  );
}
