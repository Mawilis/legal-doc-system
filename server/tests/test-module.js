const reqId = require('express-request-id');
console.log('Full module:');
console.log(reqId);
console.log('\nType of default:', typeof reqId.default);
console.log('Is default a function?', typeof reqId.default === 'function');
