import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// In development, Vite serves the React app on :5173 and forwards any request
// starting with /api to the FastAPI backend. That way the browser only ever
// talks to one origin, and we avoid CORS headaches during development.
//
// VITE_API_PROXY_TARGET lets docker-compose point the proxy at the "backend"
// container name instead of localhost.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
