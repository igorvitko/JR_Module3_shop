import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const initialForm = { username: "", email: "", password: "", password2: "" };

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setErrors(null);
    setIsSubmitting(true);
    try {
      await register(form);
      navigate("/login", { replace: true, state: { registered: true } });
    } catch (err) {
      setErrors(err.response?.data ?? { detail: "Не вдалося зареєструватися." });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <h1>Реєстрація</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Ім'я користувача</span>
          <input name="username" value={form.username} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
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
        <label className="field">
          <span>Підтвердження пароля</span>
          <input
            type="password"
            name="password2"
            value={form.password2}
            onChange={handleChange}
            required
          />
        </label>

        {errors && (
          <ul className="form-error">
            {Object.entries(errors).map(([field, messages]) => (
              <li key={field}>{Array.isArray(messages) ? messages.join(" ") : String(messages)}</li>
            ))}
          </ul>
        )}

        <button type="submit" className="button button--accent" disabled={isSubmitting}>
          {isSubmitting ? "Реєструємо…" : "Зареєструватися"}
        </button>
      </form>

      <p className="auth-switch">
        Вже є акаунт? <Link to="/login">Увійти</Link>
      </p>
    </div>
  );
}
