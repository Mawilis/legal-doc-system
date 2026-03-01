#!/* Simple mock for AuditTrail model */
export default {
  find: jest.fn().mockResolvedValue([]),
  logDocumentAccess: jest.fn().mockResolvedValue(true),
  getDocumentAccessHistory: jest.fn().mockResolvedValue([]),
};
