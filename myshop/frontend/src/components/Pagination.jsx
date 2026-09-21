export default function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav className="pagination" aria-label="Сторінки каталогу">
      <button
        type="button"
        className="button"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        ← Назад
      </button>
      <span className="pagination__status">
        Сторінка {page} з {totalPages}
      </span>
      <button
        type="button"
        className="button"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Далі →
      </button>
    </nav>
  );
}
