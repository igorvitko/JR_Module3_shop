import apiClient from "./client";

export async function fetchOrders() {
  const { data } = await apiClient.get("/orders/");
  return data;
}

export async function fetchOrder(id) {
  const { data } = await apiClient.get(`/orders/${id}/`);
  return data;
}

export async function createOrder({ shipping_address: shippingAddress, payment_method: paymentMethod }) {
  const { data } = await apiClient.post("/orders/", {
    shipping_address: shippingAddress,
    payment_method: paymentMethod,
  });
  return data;
}

export async function cancelOrder(id) {
  const { data } = await apiClient.delete(`/orders/${id}/`);
  return data;
}
