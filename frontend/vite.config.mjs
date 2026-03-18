import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "API Centrum",
        short_name: "API Centrum",
        description: "API Centrum - Domain & SSL Manager",
        theme_color: "#f5f5f7",
        background_color: "#f5f5f7",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "/pwa-192x192.png", sizes: "192x192", type: "image/png", purpose: "any maskable" },
          { src: "/pwa-512x512.png", sizes: "512x512", type: "image/png", purpose: "any maskable" },
          { src: "/icons/android-chrome-192x192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/android-chrome-512x512.png", sizes: "512x512", type: "image/png" },
        ],
      },
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue'],
          'vendor-lucide': ['lucide-vue-next']
        }
      }
    }
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, "/api"),
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
