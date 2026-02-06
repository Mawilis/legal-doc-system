// Global test setup
beforeAll(() => {
  // Increase timeout for MongoDB operations
  jest.setTimeout(30000);
  
  // Suppress console logs during tests (optional)
  if (process.env.SUPPRESS_LOGS === 'true') {
    console.log = jest.fn();
    console.error = jest.fn();
    console.warn = jest.fn();
  }
});

afterAll(() => {
  // Cleanup after all tests
});

// Global test utilities
global.sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock Date for consistent testing
global.mockDate = (dateString) => {
  const OriginalDate = global.Date;
  const mockDate = new OriginalDate(dateString);
  
  global.Date = class extends OriginalDate {
    constructor() {
      super();
      return mockDate;
    }
    
    static now() {
      return mockDate.getTime();
    }
  };
  
  return () => {
    global.Date = OriginalDate;
  };
};
