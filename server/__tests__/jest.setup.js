// Global test setup - tenant context initialization
process.env.NODE_ENV = 'test';
process.env.MONGO_URI = process.env.MONGO_URI_TEST;
console.log('Jest Setup: Test environment initialized');
