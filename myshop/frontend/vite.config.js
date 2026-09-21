import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Проксі /api на Django (localhost:8000) під час розробки — фронтенд
// звертається просто на /api/..., без хардкоду хоста в кожному запиті.
// У продакшн-збірці проксі не потрібен: там nginx сам маршрутизує
// /api/ на бекенд (буде налаштовано на Етапі 14).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
