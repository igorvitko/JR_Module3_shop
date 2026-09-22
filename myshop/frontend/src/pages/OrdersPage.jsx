import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import { cancelOrder, fetchOrders } from "../api/orders";

const STATUS_LABELS = {
  pending: "Очікує оплати",
  paid: "Оплачено",
  shipped: "Відправлено",
  delivered: "Доставлено",
  cancelled: "Скасовано",
};

// Дзеркалить Order.can_be_cancelled на бекенді (orders/models.py) — лише
// для того, щоб не показувати кнопку "Скасувати" там, де вона все одно
// поверне 403. Остаточне рішення завжди приймає сервер.
const CANCELLABLE_STATUSES = new Set(["pending", "paid"]);

export default function OrdersPage() {
  const location = useLocation();
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancellingId, setCancellingId] = useState(null);

  async function loadOrders() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchOrders();
      setOrders(data.results);
    } catch {
      setError("Не вдалося завантажити замовлення.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadOrders();
  }, []);

  async function handleCancel(orderId) {
    setCancellingId(orderId);
    try {
      await cancelOrder(orderId);
      await loadOrders();
    } catch {
      setError("Не вдалося скасувати замовлення.");
    } finally {
      setCancellingId(null);
    }
  }

  if (isLoading) {
    return <p className="muted">Завантаження…</p>;
  }

  return (
    <div className="orders-page">
      <h1>Мої замовлення</h1>

      {location.state?.justCreatedOrderId && (
        <p className="form-success">
          Замовлення #{location.state.justCreatedOrderId} успішно оформлено!
        </p>
      )}

      {error && <p className="form-error">{error}</p>}

      {orders.length === 0 ? (
        <p className="muted">У вас ще немає замовлень.</p>
      ) : (
        <ul className="order-list">
          {orders.map((order) => (
            <li key={order.id} className="order-card">
              <div className="order-card__header">
                <span>Замовлення #{order.id}</span>
                <span className={`order-status order-status--${order.status}`}>
                  {STATUS_LABELS[order.status] ?? order.status}
                </span>
              </div>

              <ul className="order-card__items">
                {order.items.map((item) => (
                  <li key={item.id}>
                    {item.product_name} × {item.quantity} — {item.price} грн/од.
                  </li>
                ))}
              </ul>

              <div className="order-card__footer">
                <span>Разом: {order.total_price} грн</span>
                <span className="muted">
                  {new Date(order.created_at).toLocaleDateString("uk-UA")}
                </span>
                {CANCELLABLE_STATUSES.has(order.status) && (
                  <button
                    type="button"
                    className="link-button"
                    disabled={cancellingId === order.id}
                    onClick={() => handleCancel(order.id)}
                  >
                    Скасувати
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
