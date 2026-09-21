import { Link, NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

const navLinks = [
  { to: "/", label: "Каталог", end: true },
  { to: "/orders", label: "Мої замовлення", requiresAuth: true },
];

export default function Header() {
  const { isAuthenticated, user, logout } = useAuth();
  const { itemCount } = useCart();

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link to="/" className="wordmark">
          Myshop
        </Link>

        <nav className="main-nav">
          {navLinks
            .filter((link) => !link.requiresAuth || isAuthenticated)
            .map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) => `main-nav__link${isActive ? " is-active" : ""}`}
              >
                {link.label}
              </NavLink>
            ))}
        </nav>

        <div className="header-actions">
          <Link to="/cart" className="cart-link">
            Кошик
            {itemCount > 0 && <span className="cart-badge">{itemCount}</span>}
          </Link>

          {isAuthenticated ? (
            <div className="account-menu">
              <Link to="/profile" className="account-menu__name">
                {user?.user?.username ?? "Профіль"}
              </Link>
              <button type="button" className="link-button" onClick={logout}>
                Вийти
              </button>
            </div>
          ) : (
            <div className="account-menu">
              <Link to="/login">Увійти</Link>
              <Link to="/register" className="button button--accent">
                Реєстрація
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
