import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true, // <--- This opens the browser automatically
    proxy: {
      '/api': {
        target: 'http://localhost:3001', // <--- FIXED: Now points to your actual backend port
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
