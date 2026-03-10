/* eslint-disable */
/**
 * client/tests/setup/setup.js
 * ESM bootstrap for Vitest
 * - idempotent
 * - jsdom initialization with graceful error message
 * - testing-library matchers and cleanup
 * - Map-backed localStorage/sessionStorage
 * - performance, raf, fetch shims
 * - __resetTestEnvironment helper
 */

import { afterEach, expect } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect'; // extends expect with jest-dom matchers
import { JSDOM } from 'jsdom';

if (typeof globalThis.__vitest_setup_done === 'undefined') {
  globalThis.__vitest_setup_done = true;

  // Initialize JSDOM if no window exists
  try {
    if (typeof globalThis.window === 'undefined') {
      const dom = new JSDOM('<!doctype html><html><body></body></html>', {
        url: 'http://localhost',
        pretendToBeVisual: true
      });
      globalThis.window = dom.window;
      globalThis.document = dom.window.document;
      globalThis.navigator = dom.window.navigator || { userAgent: 'jsdom' };
      globalThis.HTMLElement = dom.window.HTMLElement;
      globalThis.Node = dom.window.Node;
    }
  } catch (err) {
    // Clear, actionable error for missing or broken jsdom
    // Vitest will show this; non-DOM tests can still run if they don't import DOM features
    // eslint-disable-next-line no-console
    console.error('client/tests/setup/setup.js: jsdom initialization failed. Install jsdom as a dev dependency.');
    throw err;
  }

  // Ensure navigator.userAgent exists
  if (typeof globalThis.navigator === 'object' && !globalThis.navigator.userAgent) {
    globalThis.navigator.userAgent = 'jsdom';
  }

  // performance.now shim
  if (typeof globalThis.performance === 'undefined') {
    globalThis.performance = { now: () => Date.now() };
  } else if (typeof globalThis.performance.now !== 'function') {
    globalThis.performance.now = () => Date.now();
  }

  // requestAnimationFrame / cancelAnimationFrame shims
  if (typeof globalThis.requestAnimationFrame === 'undefined') {
    globalThis.requestAnimationFrame = (cb) => setTimeout(cb, 0);
  }
  if (typeof globalThis.cancelAnimationFrame === 'undefined') {
    globalThis.cancelAnimationFrame = (id) => clearTimeout(id);
  }

  // Minimal fetch polyfill (non-networking stub)
  if (typeof globalThis.fetch === 'undefined') {
    globalThis.fetch = async () => ({
      ok: false,
      status: 501,
      json: async () => ({}),
      text: async () => ''
    });
  }

  // Map-backed storage factory
  const makeStorage = () => {
    const store = new Map();
    return {
      getItem: (k) => (store.has(String(k)) ? store.get(String(k)) : null),
      setItem: (k, v) => store.set(String(k), String(v)),
      removeItem: (k) => store.delete(String(k)),
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

  // Helper to reset test environment between tests
  if (typeof globalThis.__resetTestEnvironment !== 'function') {
    globalThis.__resetTestEnvironment = () => {
      try {
        globalThis.localStorage?.clear();
        globalThis.sessionStorage?.clear();
      } catch (e) { /* ignore */ }
    };
  }

  // Ensure testing-library cleanup runs after each test
  afterEach(() => {
    try {
      cleanup();
      // reset storage between tests for isolation
      globalThis.__resetTestEnvironment();
    } catch (e) {
      // swallow cleanup errors to avoid masking test failures
    }
  });
}
