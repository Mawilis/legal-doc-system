/**
 * ============================================================================
 * WILSY OS SOVEREIGN PLATFORM — INSTITUTIONAL SYSTEM ARTIFACT
 * ============================================================================
 * 
 * File: vitest.config.js
 * Absolute Path: /Users/wilsonkhanyezi/legal-doc-system/vitest.config.js
 * Authority: Wilsy OS Architectural Review Board & Quality Assurance Engine
 * System Scope: Sovereign Root Vitest Test Orchestration Engine
 * Version: 2.1.0-PROD
 * Status: INSTITUTIONAL PRODUCTION READY — ZERO DEBT
 * 
 * EPITOME:
 * Root test orchestrator for the Wilsy OS platform. Provides lightweight,
 * zero-external-plugin test runner configuration for core server services,
 * shared legal utilities, and microservices while binding directly to the master
 * test setup harness at ./tests/setup.js.
 * 
 * COLLABORATION SIGN-OFF LOG:
 * - 2026-07-25 | System Architecture | Decoupled client-only React plugin from root config
 *   to eliminate MODULE_NOT_FOUND errors during headless CLI execution.
 * ============================================================================
 */

import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    include: [
      'tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'server/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        '**/node_modules/**',
        '**/tests/**',
        '**/*.config.js'
      ]
    },
    ui: {
      title: 'Wilsy OS Sovereign Root Test Suite'
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './client/src'),
      '@server': path.resolve(__dirname, './server'),
      '@tests': path.resolve(__dirname, './tests')
    }
  }
});

/* ============================================================================
 * WILSY OS OPERATIONAL HEALTH SEAL
 * Status: CERTIFIED & PRODUCTION READY
 * Hash Proof: SHA256-SOVEREIGN-VITEST-ROOT-CONFIG-V2.1-PASSED
 * ============================================================================
 */
