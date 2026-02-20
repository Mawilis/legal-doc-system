const database = require('./config/database');
const redis = require('./config/redis');
const queues = require('./config/queues');
const security = require('./config/security');
const auditService = require('./services/auditService');
const ClassificationService = require('./services/ClassificationService');

console.log('=== MODULE INSPECTION ===\n');

console.log('Database:');
console.log('- Type:', typeof database);
console.log('- Constructor:', database.constructor?.name);
console.log('- Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(database)).filter(p => p !== 'constructor'));
console.log('- Has healthCheck:', typeof database.healthCheck === 'function');

console.log('\nRedis:');
console.log('- Type:', typeof redis);
console.log('- Constructor:', redis.constructor?.name);
console.log('- Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(redis)).filter(p => p !== 'constructor'));
console.log('- Has healthCheck:', typeof redis.healthCheck === 'function');

console.log('\nQueues:');
console.log('- Type:', typeof queues);
console.log('- Constructor:', queues.constructor?.name);
console.log('- Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(queues)).filter(p => p !== 'constructor'));
console.log('- Has healthCheck:', typeof queues.healthCheck === 'function');

console.log('\nSecurity:');
console.log('- Type:', typeof security);
console.log('- Constructor:', security.constructor?.name);
console.log('- Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(security)).filter(p => p !== 'constructor'));
console.log('- Has healthCheck:', typeof security.healthCheck === 'function');

console.log('\nAuditService:');
console.log('- Type:', typeof auditService);
console.log('- Constructor:', auditService.constructor?.name);
console.log('- Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(auditService)).filter(p => p !== 'constructor'));
console.log('- Has healthCheck:', typeof auditService.healthCheck === 'function');

console.log('\nClassificationService:');
console.log('- Type:', typeof ClassificationService);
console.log('- Constructor:', ClassificationService.constructor?.name);
console.log('- Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(ClassificationService)).filter(p => p !== 'constructor'));
console.log('- Has healthCheck:', typeof ClassificationService.healthCheck === 'function');
