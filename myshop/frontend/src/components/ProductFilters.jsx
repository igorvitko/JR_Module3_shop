const ORDERING_OPTIONS = [
  { value: "-created_at", label: "Спочатку нові" },
  { value: "price", label: "Дешевші спочатку" },
  { value: "-price", label: "Дорожчі спочатку" },
  { value: "-popularity", label: "Популярні спочатку" },
];

export default function ProductFilters({
  categories,
  draft,
  onDraftChange,
  category,
  onCategoryChange,
  ordering,
  onOrderingChange,
}) {
  function handleDraftField(field) {
    return (event) => onDraftChange({ ...draft, [field]: event.target.value });
  }

  return (
    <div className="filters">
      <input
        type="search"
        placeholder="Пошук товарів…"
        value={draft.search}
        onChange={handleDraftField("search")}
        className="filters__search"
        aria-label="Пошук товарів"
      />

      <select
        value={category}
        onChange={(event) => onCategoryChange(event.target.value)}
        aria-label="Категорія"
      >
        <option value="">Усі категорії</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>

      <input
        type="number"
        placeholder="Ціна від"
        value={draft.minPrice}
        onChange={handleDraftField("minPrice")}
        min="0"
        aria-label="Мінімальна ціна"
      />
      <input
        type="number"
        placeholder="Ціна до"
        value={draft.maxPrice}
        onChange={handleDraftField("maxPrice")}
        min="0"
        aria-label="Максимальна ціна"
      />

      <select
        value={ordering}
        onChange={(event) => onOrderingChange(event.target.value)}
        aria-label="Сортування"
      >
        {ORDERING_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
