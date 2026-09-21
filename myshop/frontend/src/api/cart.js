import apiClient from "./client";

export async function fetchCart() {
  const { data } = await apiClient.get("/cart/");
  return data;
}

export async function addToCart(productId, quantity = 1) {
  const { data } = await apiClient.post("/cart/", { product: productId, quantity });
  return data;
}

export async function updateCartItem(productId, quantity) {
  const { data } = await apiClient.patch("/cart/", { product: productId, quantity });
  return data;
}

export async function removeFromCart(productId) {
  const { data } = await apiClient.delete("/cart/", {
    params: productId ? { product: productId } : {},
  });
  return data;
}

export async function clearCart() {
  const { data } = await apiClient.delete("/cart/");
  return data;
}
