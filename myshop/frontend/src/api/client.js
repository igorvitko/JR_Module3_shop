/**
 * Налаштований axios-клієнт для звернень до Django REST API.
 *
 * Обов'язки цього модуля:
 * 1. Підставляти Authorization: Bearer <access> в кожен запит.
 * 2. Підставляти X-Cart-Token в кожен запит (кошик гостя).
 * 3. При 401 (протух access) — один раз спробувати оновити токен через
 *    /users/login/refresh/ і повторити початковий запит.
 * 4. Запам'ятовувати X-Cart-Token з кожної відповіді /cart/, щоб фронтенд
 *    ніде більше вручну не парсив це поле.
 */
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

const ACCESS_TOKEN_KEY = "myshop_access_token";
const REFRESH_TOKEN_KEY = "myshop_refresh_token";
const CART_TOKEN_KEY = "myshop_cart_token";

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (access, refresh) => {
    if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

export const cartTokenStorage = {
  get: () => localStorage.getItem(CART_TOKEN_KEY),
  set: (token) => {
    if (token) localStorage.setItem(CART_TOKEN_KEY, token);
  },
  clear: () => localStorage.removeItem(CART_TOKEN_KEY),
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const access = tokenStorage.getAccess();
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }

  const cartToken = cartTokenStorage.get();
  if (cartToken) {
    config.headers["X-Cart-Token"] = cartToken;
  }

  return config;
});

// Кілька запитів можуть одночасно отримати 401 (наприклад, каталог і
// кошик вантажаться паралельно) — без цього кожен окремо смикнув би
// /refresh/, і другий виклик отримав би вже ротований (недійсний)
// refresh-токен. refreshPromise гарантує один спільний виклик оновлення.
let refreshPromise = null;

async function refreshAccessToken() {
  const refresh = tokenStorage.getRefresh();
  if (!refresh) {
    throw new Error("Немає refresh-токена — потрібен повторний логін.");
  }

  const response = await axios.post(`${API_BASE_URL}/users/login/refresh/`, {
    refresh,
  });
  tokenStorage.setTokens(response.data.access, response.data.refresh);
  return response.data.access;
}

apiClient.interceptors.response.use(
  (response) => {
    if (response.config.url?.includes("/cart") && response.data?.token) {
      cartTokenStorage.set(response.data.token);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const isAuthEndpoint = originalRequest?.url?.includes("/users/login");

    const shouldTryRefresh =
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthEndpoint &&
      Boolean(tokenStorage.getRefresh());

    if (!shouldTryRefresh) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }
      const newAccessToken = await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      tokenStorage.clear();
      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;
