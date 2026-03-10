import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [],
    include: ['**/tests/client/**/*.test.js'],
    exclude: ['**/node_modules/**', '**/dist/**'],
    css: true
  },
  esbuild: {
    loader: {
      '.js': 'jsx',
      '.jsx': 'jsx'
    }
  },
  resolve: {
    extensions: ['.js', '.jsx', '.json']
  }
})
