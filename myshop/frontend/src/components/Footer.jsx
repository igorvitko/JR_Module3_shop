export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer__inner">
        <span>© {new Date().getFullYear()} Myshop</span>
        <span className="site-footer__note">
          Навчальний проєкт: Django REST Framework + React
        </span>
      </div>
    </footer>
  );
}
