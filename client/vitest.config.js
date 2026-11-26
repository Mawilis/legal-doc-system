import { defineConfig, searchForWorkspaceRoot } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import fs from 'fs';

const resolveSetupFile = () => {
  const localSetup = path.resolve(__dirname, './tests/setup.js');
  const rootSetup = path.resolve(__dirname, '../tests/setup.js');
  if (fs.existsSync(localSetup)) return localSetup;
  if (fs.existsSync(rootSetup)) return rootSetup;
  return localSetup;
};

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    fs: {
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        path.resolve(__dirname, '..'),
      ],
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    // React 18's test act() is unavailable when an inherited production
    // NODE_ENV selects react.production.min.js. Set the worker environment
    // before Testing Library and React are imported; never weaken assertions.
    env: { NODE_ENV: 'test' },
    setupFiles: [resolveSetupFile()],
    include: ['tests/**/*.{test,spec}.{js,jsx}', 'src/**/*.{test,spec}.{js,jsx}'],
  },
});
