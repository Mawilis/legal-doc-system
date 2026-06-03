/* eslint-disable */
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 🛡️ ENHANCED NAVIGATION & ENVIRONMENT MOCKS
const noop = () => {};

// Mock matchMedia (Required for responsive UI/Sidebars)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Robust Location Mocking
const locationMock = {
  ...window.location,
  assign: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn(),
  href: 'http://localhost:3000/',
};

delete window.location;
window.location = locationMock;

// 🚀 SILENCE NOISY LOGS
const originalWarn = console.warn;
console.warn = (...args) => {
  if (typeof args[0] === 'string' && (
    args[0].includes('React Router Future Flag Warning') ||
    args[0].includes('The width') ||
    args[0].includes('the height')
  )) return;
  originalWarn(...args);
};

// 📊 RESIZE OBSERVER
class ResizeObserverMock {
  constructor(cb) { this.cb = cb; }
  observe() {
    if (this.cb) this.cb([{ contentRect: { width: 1024, height: 768 } }]);
  }
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserverMock;

// 🧪 CANVAS MOCK
HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  beginPath: noop, moveTo: noop, lineTo: noop, stroke: noop,
  clearRect: noop, fillRect: noop, fill: noop,
  getImageData: (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
  putImageData: noop, setTransform: noop, drawImage: noop,
  save: noop, restore: noop, canvas: { width: 1000, height: 500 },
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
