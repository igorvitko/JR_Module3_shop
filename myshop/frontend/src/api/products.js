import apiClient from "./client";

export async function fetchProducts(params = {}) {
  const { data } = await apiClient.get("/products/", { params });
  return data;
}

export async function fetchProduct(id) {
  const { data } = await apiClient.get(`/products/${id}/`);
  return data;
}

export async function fetchCategories() {
  const { data } = await apiClient.get("/categories/");
  return data;
}

export async function fetchReviews(productId) {
  const { data } = await apiClient.get(`/products/${productId}/reviews/`);
  return data;
}

export async function submitReview(productId, payload) {
  const { data } = await apiClient.post(`/products/${productId}/reviews/`, payload);
  return data;
}
