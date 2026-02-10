/* Simple mock for AuditTrail model */
module.exports = {
    find: jest.fn().mockResolvedValue([]),
    logDocumentAccess: jest.fn().mockResolvedValue(true),
    getDocumentAccessHistory: jest.fn().mockResolvedValue([])
};
