/* tests/setup.cjs - CommonJS bootstrap for Mocha */
const { JSDOM } = require('jsdom');

if (!global.window) {
  const dom = new JSDOM('<!doctype html><html><body></body></html>', {
    url: 'http://localhost',
    pretendToBeVisual: true
  });
  global.window = dom.window;
  global.document = dom.window.document;
  global.navigator = dom.window.navigator;
  global.navigator.userAgent = global.navigator.userAgent || 'jsdom';
  global.performance = global.performance || { now: () => Date.now() };
  global.requestAnimationFrame = global.requestAnimationFrame || ((cb) => setTimeout(cb, 0));
  global.cancelAnimationFrame = global.cancelAnimationFrame || ((id) => clearTimeout(id));
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
  global.localStorage = global.localStorage || makeStorage();
  global.sessionStorage = global.sessionStorage || makeStorage();
}
