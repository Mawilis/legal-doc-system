// Load test environment variables
require('dotenv').config({ path: '.env.test' });

// Validate required test environment variables
const requiredEnvVars = ['NODE_ENV'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
if (missingVars.length > 0) {
  console.error('❌ Missing required test environment variables:', missingVars.join(', '));
  process.exit(1);
}

process.env.NODE_ENV = 'test';

global.TEST_CONFIG = {
  TEST_TENANT_ID: 'test-tenant-' + Date.now(),
  TEST_USER: {
    id: 'test-user-' + Date.now(),
    email: 'test@wilsyos.co.za',
    permissions: ['legal:assess:risk', 'document:read', 'document:write'],
    role: 'TEST_ADMIN'
  }
};

console.log('✅ Test environment initialized');
