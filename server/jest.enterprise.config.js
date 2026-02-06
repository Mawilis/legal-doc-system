// Enterprise-grade Jest configuration for Wilsy OS
module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup/global-setup.js',
    '<rootDir>/tests/setup/db-mock.js',
    '<rootDir>/tests/setup/redis-mock.js',
    '<rootDir>/tests/setup/aws-mock.js'
  ],
  
  // Coverage Configuration (Investor Grade)
  collectCoverage: true,
  collectCoverageFrom: [
    '**/*.js',
    '!**/node_modules/**',
    '!**/tests/**',
    '!**/coverage/**',
    '!**/dist/**',
    '!**/.eslintrc.js',
    '!**/jest.config.js',
    '!**/webpack.config.js'
  ],
  coverageDirectory: 'coverage/epitope',
  coverageReporters: [
    'text',
    'text-summary',
    'json',
    'lcov',
    'clover',
    'html'
  ],
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './models/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    },
    './services/': {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95
    },
    './routes/': {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    }
  },
  
  // Test Structure
  testMatch: [
    '<rootDir>/tests/unit/**/*.test.js',
    '<rootDir>/tests/integration/**/*.test.js'
  ],
  
  // Module Resolution
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@models/(.*)$': '<rootDir>/models/$1',
    '^@services/(.*)$': '<rootDir>/services/$1',
    '^@routes/(.*)$': '<rootDir>/routes/$1',
    '^@middleware/(.*)$': '<rootDir>/middleware/$1',
    '^@utils/(.*)$': '<rootDir>/utils/$1',
    '^@config/(.*)$': '<rootDir>/config/$1',
    '^@tests/(.*)$': '<rootDir>/tests/$1'
  },
  
  // Performance Optimization
  maxWorkers: '50%',
  testTimeout: 30000,
  verbose: true,
  bail: 5, // Stop after 5 failures
  cacheDirectory: './.jest-cache',
  
  // Test Results
  testResultsProcessor: 'jest-sonar-reporter',
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: './reports/junit',
      outputName: 'junit.xml'
    }],
    ['jest-html-reporter', {
      pageTitle: 'Wilsy OS Test Report',
      outputPath: './reports/test-report.html',
      includeFailureMsg: true,
      includeConsoleLog: true
    }]
  ]
};
