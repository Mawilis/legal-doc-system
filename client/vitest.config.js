/**
 * TITLE: WILSY OS Client Vitest Runtime Contract
 * VERSION: v1.1.0-TEST-REACT-ENVIRONMENT
 * AUTHORITY: Frontend test harness; no Python EOS command authority.
 * EPITOME: Run browser-like React tests with a development/test React runtime
 * while preserving the separate production build and all assertions.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vitest.config.js
 * COLLABORATION / OWNERSHIP: WILSY OS Frontend Quality and EOS Engineering.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.1.0-TEST-REACT-ENVIRONMENT asserts NODE_ENV=test only in
 * Vitest workers so React Testing Library act() works under jsdom.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Test configuration only; no credentials or
 * tenant records written, read or emitted.
 * TENANT BOUNDARY: No cross-tenant authority or real tenant data.
 * AUTHORITY BOUNDARY: Tests only; Python EOS owns business authorization.
 * FINANCIAL AUTHORITY BOUNDARY: No model admission, payment or settlement.
 * FAIL-CLOSED POSTURE: Production/runtime behavior unchanged; certification
 * must fail on unmet assertions.
 */
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
/*
 * ARTIFACT: client/vitest.config.js
 * VERSION: v1.1.0-TEST-REACT-ENVIRONMENT
 * AUTHORITY BOUNDARY: Test-only React/jsdom configuration; Python EOS remains authoritative
 * TENANT POSTURE: No tenant data or grants
 * FAIL-CLOSED POSTURE: Test errors retain their failures
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
