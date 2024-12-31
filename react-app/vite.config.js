import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '192.168.1.8',
    port: 5174,
    strictPort: true,
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: 'http://192.168.1.8:8001',
        changeOrigin: true,
        secure: false
      }
    }
  },
  preview: {
    port: 5174,
    strictPort: true
  }
})
