/* eslint-env mocha */
/**
 * TEST HELPER - Loads test environment and provides utilities
 * This ensures all tests run with proper configuration
 */

const path = require('path');
const dotenv = require('dotenv');
const fs = require('fs');

// Load test environment
const envPath = path.resolve(process.cwd(), '.env.test');
if (fs.existsSync(envPath)) {
    const result = dotenv.config({ path: envPath });
    if (result.error) {
        console.error('❌ Failed to load .env.test:', result.error);
        process.exit(1);
    }
    console.log('✅ Loaded test environment from:', envPath);
} else {
    console.error('❌ .env.test not found at:', envPath);
    process.exit(1);
}

// Verify critical environment variables
const requiredVars = [
    'MONGODB_URI',
    'JWT_SECRET',
    'SECURITY_ALERT_EMAIL',
    'SECURITY_ENCRYPTION_KEY'
];

const missing = requiredVars.filter(v => !process.env[v]);
if (missing.length > 0) {
    console.error('❌ Missing required environment variables:', missing.join(', '));
    process.exit(1);
}

console.log('✅ Environment validation passed');

// Export test utilities
module.exports = {
    getTestDatabase: () => process.env.MONGODB_URI,
    getTestJWTSecret: () => process.env.JWT_SECRET,
    isTestEnv: () => process.env.NODE_ENV === 'test'
};
