// Jest setup file
process.env.NODE_ENV = 'test';
process.env.PORT = 3002; // Use different port for tests

// Global test setup
global.__TEST__ = true;

// Mock console for cleaner test output
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
};
