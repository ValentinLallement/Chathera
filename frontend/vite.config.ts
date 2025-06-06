import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss(), react()],
  build: {
    assetsDir: 'static', // Place assets in a 'static/' folder
  },
  server: {
    port: 5173,
    proxy: {
      // Any request starting with /api will be forwarded as-is to http://127.0.0.1:8000
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        // no rewrite needed, since your backend routes are /api/auth/…
      },
    },
  },
})

/*
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss(), react()],
  build: {
    assetsDir: 'static', 
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    allowedHosts: [
      '*',

    ],
  }
})

*/