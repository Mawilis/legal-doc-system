module.exports = {
  testEnvironment: 'node',
  verbose: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  
  // Force module resolution
  moduleDirectories: ['node_modules', 'server'],
  
  // Clear cache between runs
  cache: false,
  
  // Module name mapping to force correct file
  moduleNameMapper: {
    '^@utils/cryptoUtils$': '<rootDir>/server/utils/forensic/forensicCrypto.js'
  },
  
  // Test match patterns
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/?(*.)+(spec|test).js'
  ],
  
  // Transform ignore patterns
  transformIgnorePatterns: ['/node_modules/'],
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/server/__tests__/setup.js']
};
