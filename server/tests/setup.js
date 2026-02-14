/* eslint-env jest */
/**
 * Test Setup Helper
 * 
 * This file runs before all tests to set up the test environment,
 * mock external dependencies, and configure encryption keys.
 */

const path = require('path');
const dotenv = require('dotenv');

// Load test environment variables
dotenv.config({ path: path.join(__dirname, '../.env.test') });

// Set test environment
process.env.NODE_ENV = 'test';

// Ensure encryption keys are set for cryptoUtils
if (!process.env.USER_DATA_ENCRYPTION_KEY) {
    process.env.USER_DATA_ENCRYPTION_KEY = 'test-data-encryption-key-32-bytes-long!!';
}
if (!process.env.USER_PII_ENCRYPTION_KEY) {
    process.env.USER_PII_ENCRYPTION_KEY = 'test-pii-encryption-key-32-bytes-long!!';
}

// Mock console methods to keep test output clean
global.console = {
    ...console,
    log: jest.fn(),
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
};

// Increase timeout for all tests
jest.setTimeout(30000);

// Global afterAll hook to clean up
afterAll(async () => {
    // Add any cleanup here
    jest.clearAllMocks();
    jest.resetAllMocks();
});
