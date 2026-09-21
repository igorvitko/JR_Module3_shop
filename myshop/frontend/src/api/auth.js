import apiClient, { tokenStorage } from "./client";

export async function register({ username, email, password, password2 }) {
  const { data } = await apiClient.post("/users/register/", {
    username,
    email,
    password,
    password2,
  });
  return data;
}

export async function login({ username, password }) {
  const { data } = await apiClient.post("/users/login/", { username, password });
  tokenStorage.setTokens(data.access, data.refresh);
  return data;
}

export function logout() {
  tokenStorage.clear();
}

export async function fetchProfile() {
  const { data } = await apiClient.get("/users/profile/");
  return data;
}

export async function updateProfile(payload) {
  const { data } = await apiClient.patch("/users/profile/", payload);
  return data;
}

export async function changePassword(payload) {
  const { data } = await apiClient.post("/users/change-password/", payload);
  return data;
}
