require('dotenv').config({ path: './.env.test' });

module.exports = {
    testEnvironment: 'node',
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
    verbose: true,
    detectOpenHandles: true,
    forceExit: true,
    testTimeout: 30000
};
