module.exports = {
    moduleNameMapper: {
        '^@services/(.*)$': '<rootDir>/src/services/$1',
        '^.+\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    },
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
    transform: {
        '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
    },
};
