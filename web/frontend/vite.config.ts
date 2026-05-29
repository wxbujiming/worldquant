import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5170,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8987",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://127.0.0.1:8987",
        ws: true,
      },
    },
  },
});
