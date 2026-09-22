import { useEffect, useState } from "react";

import { changePassword, updateProfile } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function ProfilePage() {
  const { user, refreshProfile } = useAuth();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    default_shipping_address: "",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  const [passwordForm, setPasswordForm] = useState({
    old_password: "",
    new_password: "",
    new_password2: "",
  });
  const [passwordStatus, setPasswordStatus] = useState(null);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  useEffect(() => {
    if (!user) return;
    setForm({
      first_name: user.user?.first_name ?? "",
      last_name: user.user?.last_name ?? "",
      email: user.user?.email ?? "",
      phone: user.phone ?? "",
      default_shipping_address: user.default_shipping_address ?? "",
    });
  }, [user]);

  function handleFieldChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaveStatus(null);
    setIsSaving(true);
    try {
      await updateProfile({
        user: {
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
        },
        phone: form.phone,
        default_shipping_address: form.default_shipping_address,
      });
      await refreshProfile();
      setSaveStatus({ type: "success", message: "Профіль оновлено." });
    } catch {
      setSaveStatus({ type: "error", message: "Не вдалося зберегти зміни." });
    } finally {
      setIsSaving(false);
    }
  }

  function handlePasswordFieldChange(event) {
    const { name, value } = event.target;
    setPasswordForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handlePasswordSubmit(event) {
    event.preventDefault();
    setPasswordStatus(null);
    setIsChangingPassword(true);
    try {
      await changePassword(passwordForm);
      setPasswordForm({ old_password: "", new_password: "", new_password2: "" });
      setPasswordStatus({ type: "success", message: "Пароль змінено." });
    } catch (err) {
      const data = err.response?.data ?? {};
      const message =
        data.old_password?.[0] ??
        data.new_password2?.[0] ??
        data.new_password?.[0] ??
        "Не вдалося змінити пароль.";
      setPasswordStatus({ type: "error", message });
    } finally {
      setIsChangingPassword(false);
    }
  }

  if (!user) {
    return <p className="muted">Завантаження…</p>;
  }

  return (
    <div className="profile-page">
      <h1>Особистий кабінет</h1>

      <section className="profile-section">
        <h2>Дані профілю</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Ім'я</span>
            <input name="first_name" value={form.first_name} onChange={handleFieldChange} />
          </label>
          <label className="field">
            <span>Прізвище</span>
            <input name="last_name" value={form.last_name} onChange={handleFieldChange} />
          </label>
          <label className="field">
            <span>Email</span>
            <input type="email" name="email" value={form.email} onChange={handleFieldChange} />
          </label>
          <label className="field">
            <span>Телефон</span>
            <input name="phone" value={form.phone} onChange={handleFieldChange} />
          </label>
          <label className="field">
            <span>Адреса доставки за замовчуванням</span>
            <textarea
              name="default_shipping_address"
              rows={2}
              value={form.default_shipping_address}
              onChange={handleFieldChange}
            />
          </label>

          {saveStatus && (
            <p className={saveStatus.type === "error" ? "form-error" : "form-success"}>
              {saveStatus.message}
            </p>
          )}

          <button type="submit" className="button button--accent" disabled={isSaving}>
            {isSaving ? "Зберігаємо…" : "Зберегти зміни"}
          </button>
        </form>
      </section>

      <section className="profile-section">
        <h2>Зміна пароля</h2>
        <form className="auth-form" onSubmit={handlePasswordSubmit}>
          <label className="field">
            <span>Поточний пароль</span>
            <input
              type="password"
              name="old_password"
              value={passwordForm.old_password}
              onChange={handlePasswordFieldChange}
              required
            />
          </label>
          <label className="field">
            <span>Новий пароль</span>
            <input
              type="password"
              name="new_password"
              value={passwordForm.new_password}
              onChange={handlePasswordFieldChange}
              required
            />
          </label>
          <label className="field">
            <span>Підтвердження нового пароля</span>
            <input
              type="password"
              name="new_password2"
              value={passwordForm.new_password2}
              onChange={handlePasswordFieldChange}
              required
            />
          </label>

          {passwordStatus && (
            <p className={passwordStatus.type === "error" ? "form-error" : "form-success"}>
              {passwordStatus.message}
            </p>
          )}

          <button type="submit" className="button" disabled={isChangingPassword}>
            {isChangingPassword ? "Змінюємо…" : "Змінити пароль"}
          </button>
        </form>
      </section>
    </div>
  );
}
