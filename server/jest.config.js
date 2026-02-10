module.exports = {
  testEnvironment: 'node',
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/tests/**/*.test.js',
    '**/*.test.js',
    '**/market-intelligence/**/*.test.js',
    '**/global-expansion/**/*.test.js',
    '**/patents/**/*.test.js',
    '**/investor-materials/**/*.test.js'
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
    '/coverage/'
  ],
  collectCoverageFrom: [
    'services/**/*.js',
    'utils/**/*.js',
    'middleware/**/*.js',
    'models/**/*.js',
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/setupAfterEnv.js'],
  verbose: true,
  detectOpenHandles: true,
  forceExit: true
};
