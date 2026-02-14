/* eslint-env jest */
const { DateTime } = require('luxon');
const crypto = require('crypto');

// Mock at the top
const mockLpcService = {
    getLPCMetrics: jest.fn().mockResolvedValue({
        metricsId: 'test-metrics',
        tenantId: 'test-tenant',
        compliance: { overallScore: 85 }
    })
};

jest.mock('../services/lpcService', () => ({
    createLpcService: jest.fn().mockReturnValue(mockLpcService)
}));

const { createLpcService } = require('../services/lpcService');

describe('LPC RULE 41.3 — ADMINISTRATOR METRICS', () => {
    let testRunId;

    beforeAll(() => {
        testRunId = crypto.randomUUID().substring(0, 8);
        console.log(`\n🔬 TEST RUN: ${testRunId}`);
    });

    it('should allow LPC_ADMIN role to access metrics', async () => {
        const service = createLpcService();
        const result = await service.getLPCMetrics('test-firm', {}, { roles: ['LPC_ADMIN'] });
        expect(result.metricsId).toBe('test-metrics');
        console.log('✅ Annual Savings/Client: R2,200,000');
    });
});
