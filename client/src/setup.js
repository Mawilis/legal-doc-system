/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  ████████╗███████╗███████╗████████╗    ███████╗███████╗████████╗██╗   ██╗██████╗ ║
  ║  ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗║
  ║     ██║   █████╗  ███████╗   ██║       ███████╗█████╗     ██║   ██║   ██║██████╔╝║
  ║     ██║   ██╔══╝  ╚════██║   ██║       ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝ ║
  ║     ██║   ███████╗███████║   ██║       ███████║███████╗   ██║   ╚██████╔╝██║     ║
  ║     ╚═╝   ╚══════╝╚══════╝   ╚═╝       ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ║
  ║                                                                                   ║
  ║  🏛️  WILSY OS 2050 - TEST SETUP (PRESERVING EXISTING LOGIC)                      ║
  ║  ⚖️  The Global Legal Operating System - 10th Generation                         ║
  ║                                                                                   ║
  ║  ├─ PRESERVED: crypto.randomUUID → 'test-uuid-12345'                              ║
  ║  ├─ PRESERVED: window.location.href → 'http://localhost:5173'                     ║
  ║  ├─ PRESERVED: window.location.origin → 'http://localhost:5173'                   ║
  ║  ├─ ADDED: Full localStorage mocking (non-destructive)                            ║
  ║  ├─ ADDED: sessionStorage mocking                                                  ║
  ║  ├─ ADDED: matchMedia mocking                                                      ║
  ║  └─ ADDED: Enhanced crypto with subtle.digest                                      ║
  ║                                                                                   ║
  ║  "Preserve the logic. Enhance the capability. Never break what works."           ║
  ╚═══════════════════════════════════════════════════════════════════════════════════╝*/

import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// ============================================================================
// PRESERVED EXISTING LOGIC - DO NOT MODIFY THIS SECTION
// ============================================================================

// Extend Vitest's expect with testing-library matchers (PRESERVED)
expect.extend(matchers)

// Cleanup after each test (PRESERVED)
afterEach(() => {
  cleanup()
})

// ============================================================================
// ENHANCED MOCKS - PRESERVING EXISTING VALUES, ADDING FUNCTIONALITY
// ============================================================================

/**
 * Mock crypto for tests
 * PRESERVES: randomUUID returns 'test-uuid-12345'
 * PRESERVES: getRandomValues returns array
 * ADDS: subtle.digest for async crypto operations
 */
Object.defineProperty(global, 'crypto', {
  value: {
    // EXISTING - KEPT EXACTLY AS IS
    randomUUID: () => 'test-uuid-12345',
    // EXISTING - KEPT EXACTLY AS IS
    getRandomValues: (arr) => arr,
    // ADDED - Enhances without breaking existing tests
    subtle: {
      digest: async () => new ArrayBuffer(32)
    }
  },
  writable: true,
  configurable: true
})

/**
 * Mock window.location
 * PRESERVES: href 'http://localhost:5173'
 * PRESERVES: origin 'http://localhost:5173'
 * ADDS: Additional location properties for compatibility
 */
Object.defineProperty(window, 'location', {
  value: {
    // EXISTING - KEPT EXACTLY AS IS
    href: 'http://localhost:5173',
    // EXISTING - KEPT EXACTLY AS IS
    origin: 'http://localhost:5173',
    // ADDED - Enhances without breaking existing tests
    pathname: '/',
    search: '',
    hash: '',
    assign: vi.fn(),
    replace: vi.fn(),
    reload: vi.fn()
  },
  writable: true,
  configurable: true
})

// ============================================================================
// ADDITIONAL MOCKS - NON-DESTRUCTIVE ENHANCEMENTS
// ============================================================================

/**
 * Mock localStorage with complete implementation
 * ADDED - Does not interfere with existing tests
 */
class LocalStorageMock {
  constructor() {
    this.store = {}
  }
  clear() { this.store = {} }
  getItem(key) { return this.store[key] || null }
  setItem(key, value) { this.store[key] = value.toString() }
  removeItem(key) { delete this.store[key] }
  key(index) { return Object.keys(this.store)[index] || null }
  get length() { return Object.keys(this.store).length }
}

// Only define if not already defined (preserves any existing mock)
if (!window.localStorage) {
  Object.defineProperty(window, 'localStorage', {
    value: new LocalStorageMock(),
    writable: true,
    configurable: true
  })
}

/**
 * Mock sessionStorage
 * ADDED - Non-destructive enhancement
 */
if (!window.sessionStorage) {
  Object.defineProperty(window, 'sessionStorage', {
    value: new LocalStorageMock(),
    writable: true,
    configurable: true
  })
}

/**
 * Mock matchMedia for component tests
 * ADDED - Non-destructive enhancement
 */
if (!window.matchMedia) {
  Object.defineProperty(window, 'matchMedia', {
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn()
    })),
    writable: true,
    configurable: true
  })
}

// ============================================================================
// ARCHITECT'S VERIFICATION
// ============================================================================
// ✅ EXISTING LOGIC PRESERVED: crypto.randomUUID → 'test-uuid-12345'
// ✅ EXISTING LOGIC PRESERVED: window.location.href → 'http://localhost:5173'
// ✅ EXISTING LOGIC PRESERVED: window.location.origin → 'http://localhost:5173'
// ✅ EXISTING LOGIC PRESERVED: afterEach cleanup
// ✅ EXISTING LOGIC PRESERVED: matchers extended
//
// 🏛️  WILSY OS 2050 - TEST SETUP ENHANCED
// ⚖️  Supreme Architect: Wilson Khanyezi
// 📅  Generation: 10
// 🔒  "Never break what works. Only add what's needed."
// ============================================================================
