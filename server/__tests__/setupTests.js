/* eslint-env jest */

// Global setup for Jest tests
beforeAll(() => {
  // Setup before all tests
  console.log('Jest setup running...');
});

beforeEach(() => {
  // Reset mocks before each test
  jest.clearAllMocks();
});

afterAll(() => {
  // Cleanup after all tests
  console.log('Jest cleanup complete');
});

// Mock console for cleaner test output
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};
