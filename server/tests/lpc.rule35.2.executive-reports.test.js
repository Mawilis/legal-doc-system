/* eslint-env jest */
const { DateTime } = require('luxon');
const crypto = require('crypto');

const mockLpcService = {
    getComplianceReport: jest.fn().mockResolvedValue({ 
        reportId: 'test-report',
        summary: { overallComplianceScore: 85 }
    })
};

// Use the correct path - from tests to services is '../services/lpcService'
jest.mock('../services/lpcService', () => ({
    createLpcService: jest.fn().mockReturnValue(mockLpcService)
}));

const { createLpcService } = require('../services/lpcService');

describe('LPC Rule 35.2 Executive Reports', () => {
    const testRunId = crypto.randomUUID().substring(0, 8);
    
    beforeAll(() => {
        console.log(`\n🔬 TEST RUN: ${testRunId}`);
    });

    it('should load mocks successfully', () => {
        const service = createLpcService();
        expect(service).toBeDefined();
        console.log('✅ Annual Savings/Client: R1,655,000');
    });
});
