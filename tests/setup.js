/* eslint-disable */
/**
 * tests/setup.js
 * Robust test environment bootstrap for client-side tests (JSDOM + storage + hooks)
 *
 * Usage:
 *   mocha --require tests/setup.js ...
 *   or set "mocha.opts" / "test" script to require this file.
 */

import { JSDOM } from 'jsdom';

if (!globalThis.window) {
  const dom = new JSDOM('<!doctype html><html><body></body></html>', {
    url: 'http://localhost',
    pretendToBeVisual: true
  });

  // Basic DOM
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  globalThis.navigator = dom.window.navigator;

  // Provide a stable userAgent for fingerprinting/tests
  if (!globalThis.navigator.userAgent) {
    globalThis.navigator.userAgent = 'jsdom/16 (testing)';
  }

  // performance shim
  if (typeof globalThis.performance === 'undefined') {
    globalThis.performance = {
      now: () => Date.now()
    };
  } else if (typeof globalThis.performance.now !== 'function') {
    globalThis.performance.now = () => Date.now();
  }

  // requestAnimationFrame shim
  if (typeof globalThis.requestAnimationFrame === 'undefined') {
    globalThis.requestAnimationFrame = (cb) => setTimeout(cb, 0);
    globalThis.cancelAnimationFrame = (id) => clearTimeout(id);
  }

  // Minimal fetch polyfill (node environment)
  if (typeof globalThis.fetch === 'undefined') {
    globalThis.fetch = async () => {
      return {
        ok: false,
        status: 501,
        json: async () => ({})
      };
    };
  }

  // Map-backed localStorage/sessionStorage (deterministic, test-friendly)
  const makeStorage = () => {
    const store = new Map();
    return {
      getItem: (k) => (store.has(k) ? store.get(k) : null),
      setItem: (k, v) => store.set(String(k), String(v)),
      removeItem: (k) => store.delete(k),
      clear: () => store.clear(),
      _store: store
    };
  };

  if (typeof globalThis.localStorage === 'undefined') {
    globalThis.localStorage = makeStorage();
  }

  if (typeof globalThis.sessionStorage === 'undefined') {
    globalThis.sessionStorage = makeStorage();
  }
}

// Ensure React hooks act environment is enabled if available
try {
  // dynamic import to avoid hard failure if package missing
  // eslint-disable-next-line import/no-extraneous-dependencies
  const { enableActEnvironment } = await import('@testing-library/react-hooks');
  if (typeof enableActEnvironment === 'function') {
    enableActEnvironment(true);
  }
} catch (e) {
  // Not fatal: tests that need react-hooks will import their own setup or fail with a clear error.
  // Keep silent to avoid noisy logs in environments without the package.
}
