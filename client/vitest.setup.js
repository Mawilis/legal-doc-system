/* eslint-disable */
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 🚀 SILENCE REACT ROUTER & RECHARTS NOISE
const originalWarn = console.warn;
console.warn = (...args) => {
  if (typeof args[0] === 'string' && (
    args[0].includes('React Router Future Flag Warning') ||
    args[0].includes('The width') ||
    args[0].includes('the height')
  )) return;
  originalWarn(...args);
};

// 📊 AGGRESSIVE GEOMETRY MOCK
// Forces Recharts to believe it has a valid 1000px container
class ResizeObserverMock {
  constructor(cb) {
    this.cb = cb;
  }
  observe() {
    // Immediately trigger a resize event with fake dimensions
    this.cb([{ contentRect: { width: 1000, height: 500 } }]);
  }
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserverMock;

// 🏛️ CANVAS API FORENSIC MOCK
HTMLCanvasElement.prototype.getContext = vi.fn((type) => {
  if (type === '2d') {
    return {
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      clearRect: vi.fn(),
      getImageData: vi.fn((x, y, w, h) => ({
        data: new Uint8ClampedArray(w * h * 4),
        width: w,
        height: h
      })),
      putImageData: vi.fn(),
      setTransform: vi.fn(),
      drawImage: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      canvas: { width: 1000, height: 150 },
    };
  }
  return null;
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
