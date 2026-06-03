/* eslint-disable */
// Test setup for ES modules
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Set up global variables for tests
global.__dirname = __dirname;
global.__filename = __filename;

// Mock the auditLogger for tests if needed
if (process.env.NODE_ENV === 'test') {
  console.log('[TEST] Setting up test environment...');
}
