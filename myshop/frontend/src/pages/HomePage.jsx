import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchCategories, fetchProducts } from "../api/products";
import Pagination from "../components/Pagination";
import ProductCard from "../components/ProductCard";
import ProductFilters from "../components/ProductFilters";
import { useDebouncedValue } from "../hooks/useDebouncedValue";

const PAGE_SIZE = 12;

export default function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [count, setCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const category = searchParams.get("category") ?? "";
  const ordering = searchParams.get("ordering") ?? "-created_at";
  const page = Number(searchParams.get("page") ?? "1");

  // Пошук і ціни — з debounce, щоб не смикати API на кожну клавішу.
  const [draft, setDraft] = useState({
    search: searchParams.get("search") ?? "",
    minPrice: searchParams.get("min_price") ?? "",
    maxPrice: searchParams.get("max_price") ?? "",
  });
  const debouncedDraft = useDebouncedValue(draft, 400);

  function updateParams(patch) {
    const next = new URLSearchParams(searchParams);
    Object.entries(patch).forEach(([key, value]) => {
      if (value === null || value === "") {
        next.delete(key);
      } else {
        next.set(key, String(value));
      }
    });
    setSearchParams(next);
  }

  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    updateParams({
      search: debouncedDraft.search || null,
      min_price: debouncedDraft.minPrice || null,
      max_price: debouncedDraft.maxPrice || null,
      page: null,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedDraft]);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    const params = { page, ordering };
    if (searchParams.get("search")) params.search = searchParams.get("search");
    if (category) params.category = category;
    if (searchParams.get("min_price")) params.min_price = searchParams.get("min_price");
    if (searchParams.get("max_price")) params.max_price = searchParams.get("max_price");

    fetchProducts(params)
      .then((data) => {
        if (cancelled) return;
        setProducts(data.results);
        setCount(data.count);
      })
      .catch(() => {
        if (!cancelled) setError("Не вдалося завантажити товари. Спробуйте оновити сторінку.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, category, ordering, page]);

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE));

  return (
    <div className="catalog-page">
      <h1>Каталог товарів</h1>

      <ProductFilters
        categories={categories}
        draft={draft}
        onDraftChange={setDraft}
        category={category}
        onCategoryChange={(value) => updateParams({ category: value || null, page: null })}
        ordering={ordering}
        onOrderingChange={(value) => updateParams({ ordering: value, page: null })}
      />

      {error && <p className="form-error">{error}</p>}

      {isLoading ? (
        <p className="muted">Завантаження…</p>
      ) : products.length === 0 ? (
        <p className="muted">Нічого не знайдено за вашим запитом.</p>
      ) : (
        <>
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          <Pagination
            page={page}
            totalPages={totalPages}
            onPageChange={(nextPage) =>
              updateParams({ page: nextPage === 1 ? null : nextPage })
            }
          />
        </>
      )}
    </div>
  );
}
