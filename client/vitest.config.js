import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.js'],
    include: ['**/tests/client/**/*.test.js'],
    exclude: ['**/node_modules/**', '**/dist/**'],
  },
  resolve: {
    extensions: ['.js', '.jsx', '.json']
  }
})
