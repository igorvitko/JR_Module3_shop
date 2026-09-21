import { useParams } from "react-router-dom";

/** Сторінка товару (опис, відгуки, "Додати в кошик"). Наповнення — Етап 11. */
export default function ProductDetailPage() {
  const { id } = useParams();

  return (
    <div className="placeholder-page">
      <h1>Товар #{id}</h1>
      <p>Деталі товару та відгуки зʼявляться тут на наступному етапі.</p>
    </div>
  );
}
