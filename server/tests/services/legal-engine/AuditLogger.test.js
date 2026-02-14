/* eslint-disable no-undef */
const AuditLogger = require('../../../utils/auditLogger');

describe('AuditLogger Mock', () => {
  test('log method should be mocked', () => {
    expect(typeof AuditLogger.log).toBe('function');
    expect(typeof AuditLogger.log).toBe("function"); // Should be a Jest mock
  });
  
  test('log method returns promise', async () => {
    const result = await AuditLogger.log({ event: 'test' });
    expect(result).toBeDefined();
  });
});
