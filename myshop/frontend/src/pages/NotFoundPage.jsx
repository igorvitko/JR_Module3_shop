import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="placeholder-page">
      <h1>Сторінку не знайдено</h1>
      <p>
        Такої адреси немає. <Link to="/">Повернутися в каталог</Link>.
      </p>
    </div>
  );
}
