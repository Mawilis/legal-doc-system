// Debug script to see what's actually being imported
const cryptoUtils = require('./server/utils/cryptoUtils');
console.log('=== IMPORT DEBUG ===');
console.log('Import path:', require.resolve('./server/utils/cryptoUtils'));
console.log('Exported keys:', Object.keys(cryptoUtils));
console.log('\nFirst few lines of actual file:');
console.log('---');
const fs = require('fs');
const content = fs.readFileSync('./server/utils/cryptoUtils.js', 'utf8').split('\n').slice(0, 10).join('\n');
console.log(content);
console.log('---');
