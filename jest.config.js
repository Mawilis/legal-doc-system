module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/server/__tests__/setup.js'],
  testPathIgnorePatterns: ['/node_modules/', '/services/'],
  modulePathIgnorePatterns: ['/services/'],
  moduleDirectories: ['node_modules', 'server'],
  verbose: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  // Use testMatch ONLY (removed testRegex)
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/?(*.)+(spec|test).js'
  ]
};
