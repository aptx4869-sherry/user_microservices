import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/config': 'http://localhost:8000',
      '/google-register': 'http://localhost:8000',
      '/cookie-validate': 'http://localhost:8000',
      '/google-client-id': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
    },
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
      'Cross-Origin-Embedder-Policy': 'unsafe-none',
    }
  }
});
