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

// DON'T mock console - it breaks Mongoose
// Keep console intact
