import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
  ],
  optimizeDeps: {
    include: ['lucide-react'],
  },
  server: {
    port: 3737,
    proxy: {
      '/api': {
        target: 'http://localhost:8181',
        changeOrigin: true,
      },
    },
  },
})
