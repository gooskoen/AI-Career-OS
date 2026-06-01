import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/auth": "http://localhost:8000",
      "/reporting": "http://localhost:8000",
      "/applications": "http://localhost:8000",
      "/candidates": "http://localhost:8000",
      "/jobs": "http://localhost:8000",
      "/matches": "http://localhost:8000",
      "/outcomes": "http://localhost:8000",
      "/insights": "http://localhost:8000"
    }
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts"
  }
});
