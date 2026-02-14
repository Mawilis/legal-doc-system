/* eslint-env jest */
/**
 * Test file to verify lpcService can be imported
 */

// Load environment variables first
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env.test') });

// Set required environment variables if not set by dotenv
process.env.USER_DATA_ENCRYPTION_KEY = process.env.USER_DATA_ENCRYPTION_KEY || 'test-data-encryption-key-32-bytes-long!!';
process.env.USER_PII_ENCRYPTION_KEY = process.env.USER_PII_ENCRYPTION_KEY || 'test-pii-encryption-key-32-bytes-long!!';
process.env.LPC_API_BASE_URL = process.env.LPC_API_BASE_URL || 'https://test-api.lpc.org.za/v2';
process.env.LPC_API_KEY = process.env.LPC_API_KEY || 'test-lpc-api-key-2026-02-14-validation';

describe('LPC Service Import Test', () => {
    it('should import lpcService without errors', () => {
        expect(() => {
            const lpcService = require('../services/lpcService');
            expect(lpcService).toBeDefined();
            console.log('✅ lpcService imported successfully');
            console.log('Exports:', Object.keys(lpcService));
        }).not.toThrow();
    });
});
