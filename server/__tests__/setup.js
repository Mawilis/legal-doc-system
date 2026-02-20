// Global test setup
process.env.NODE_ENV = 'test';
jest.setTimeout(30000);

// Clear require cache before each test
beforeEach(() => {
  jest.resetModules();
  jest.clearAllMocks();
});
