/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - GLOBAL VITEST TEST ENVIRONMENT SETUP                                                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 55.1.0-MARS-BIBLICAL | PRODUCTION READY | GLOBAL TEST HARNESS                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE                                                          ║
 * ║ FILE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/setup.js                                                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { cleanup } from '@testing-library/react';
import { vi, afterEach } from 'vitest';

// Safely register jest-dom matchers if present in the runtime environment
try {
  import('@testing-library/jest-dom');
} catch (e) {
  // Silent fallback for non-DOM headless environments
}

// Global teardown and DOM cleanup after every test execution
afterEach(() => {
  if (typeof window !== 'undefined') {
    cleanup();
  }
  vi.clearAllMocks();
});
