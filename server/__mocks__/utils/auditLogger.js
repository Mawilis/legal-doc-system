/* Simple mock for auditLogger to avoid mongoose dependency */
export default {
  audit: jest.fn().mockResolvedValue(true),
  logSecurityEvent: jest.fn().mockResolvedValue(true),
  logDocumentAccess: jest.fn().mockResolvedValue(true),
};
