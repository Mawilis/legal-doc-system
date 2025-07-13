// server/tests/test-setup-env.js
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables specifically from our .env.test file
// This ensures they are available globally to all test suites.
dotenv.config({ path: path.resolve(__dirname, '../server/.env.test') });
