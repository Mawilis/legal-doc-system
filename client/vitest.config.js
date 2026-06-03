import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.js',
    // 🛡️ Updated to capture the new forensic test directory
    include: ['tests/client/**/*.{test,spec}.{js,jsx}'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/setup.js'],
    },
  },
  resolve: {
    alias: {
      // Allows for cleaner forensic imports if you choose to use them
      '@': path.resolve(__dirname, './src'),
    },
  },
});
