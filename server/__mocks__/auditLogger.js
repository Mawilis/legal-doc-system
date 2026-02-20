/* eslint-env jest */

const mockAuditLog = [];

const auditLogger = {
    log: jest.fn((entry) => {
        // Add retention metadata to all log entries
        const logEntry = {
            ...entry,
            timestamp: new Date().toISOString(),
            logId: Math.random().toString(36).substring(7),
            metadata: {
                ...entry.metadata,
                retentionPolicy: entry.metadata?.retentionPolicy || 'companies_act_10_years',
                dataResidency: entry.metadata?.dataResidency || 'ZA',
                retentionStart: entry.metadata?.retentionStart || new Date().toISOString(),
                forensicEvidence: entry.metadata?.forensicEvidence !== undefined ? entry.metadata.forensicEvidence : true
            }
        };
        mockAuditLog.push(logEntry);
        return Promise.resolve(logEntry);
    }),
    audit: jest.fn((entry) => {
        const logEntry = {
            ...entry,
            timestamp: new Date().toISOString(),
            logId: Math.random().toString(36).substring(7),
            metadata: {
                ...entry.metadata,
                retentionPolicy: entry.metadata?.retentionPolicy || 'companies_act_10_years',
                dataResidency: entry.metadata?.dataResidency || 'ZA',
                retentionStart: entry.metadata?.retentionStart || new Date().toISOString(),
                forensicEvidence: entry.metadata?.forensicEvidence !== undefined ? entry.metadata.forensicEvidence : true
            }
        };
        mockAuditLog.push(logEntry);
        return Promise.resolve(logEntry);
    }),
    getLogs: jest.fn(() => mockAuditLog),
    clearLogs: jest.fn(() => {
        mockAuditLog.length = 0;
    })
};

module.exports = auditLogger;
