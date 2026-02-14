module.exports = {
    testEnvironment: 'node',
    testMatch: [
        '**/tests/**/*.test.js',
        '**/__tests__/**/*.test.js'
    ],
    testPathIgnorePatterns: [
        '/node_modules/',
        '/dist/'
    ],
    moduleFileExtensions: ['js', 'json'],
    verbose: true,
    testTimeout: 30000,
    maxWorkers: 1,
    clearMocks: true,
    resetMocks: false,
    restoreMocks: false
};
