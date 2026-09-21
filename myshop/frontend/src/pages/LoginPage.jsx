import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname ?? "/";

  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(form);
      navigate(redirectTo, { replace: true });
    } catch {
      setError("Неправильний логін або пароль.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <h1>Вхід</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Ім'я користувача</span>
          <input name="username" value={form.username} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Пароль</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>

        {error && <p className="form-error">{error}</p>}

        <button type="submit" className="button button--accent" disabled={isSubmitting}>
          {isSubmitting ? "Входимо…" : "Увійти"}
        </button>
      </form>

      <p className="auth-switch">
        Ще немає акаунту? <Link to="/register">Зареєструватися</Link>
      </p>
    </div>
  );
}
