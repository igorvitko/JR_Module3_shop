import { Link } from "react-router-dom";

export default function ProductCard({ product }) {
  return (
    <Link to={`/products/${product.id}`} className="product-card">
      <div className="product-card__image">
        {product.image ? (
          <img src={product.image} alt={product.name} />
        ) : (
          <div className="product-card__image-placeholder" aria-hidden="true" />
        )}
      </div>
      <div className="product-card__body">
        <h3 className="product-card__name">{product.name}</h3>
        <p className="product-card__price">{product.price} грн</p>
        {product.average_rating != null && (
          <p className="product-card__rating">★ {product.average_rating.toFixed(1)}</p>
        )}
        {!product.is_in_stock && (
          <p className="product-card__out-of-stock">Немає в наявності</p>
        )}
      </div>
    </Link>
  );
}
