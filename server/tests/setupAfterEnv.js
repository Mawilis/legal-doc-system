// Mock logger
jest.mock('../utils/logger', () => ({
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  debug: jest.fn(),
  child: jest.fn(() => ({
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn()
  }))
}));

// Mock AuditLogger
jest.mock('../utils/auditLogger', () => ({
  log: jest.fn(() => Promise.resolve(true))
}));

// Global test utilities
global.createTestContext = (overrides = {}) => ({
  tenantId: global.TEST_CONFIG.TEST_TENANT_ID,
  user: global.TEST_CONFIG.TEST_USER,
  ...overrides
});

afterEach(() => {
  jest.clearAllMocks();
});

afterAll(() => {
  console.log('🧹 Test cleanup completed');
});

// Add createTestContext if not already there
if (!global.createTestContext) {
  global.createTestContext = (overrides = {}) => ({
    tenantId: 'test-tenant-' + Date.now(),
    user: {
      id: 'test-user-' + Date.now(),
      email: 'test@wilsyos.co.za',
      permissions: ['legal:assess:risk', 'document:read', 'document:write'],
      role: 'TEST_ADMIN'
    },
    ...overrides
  });
}
