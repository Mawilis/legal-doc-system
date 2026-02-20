const path = require('path');
console.log('Jest module resolution debug:');
console.log('Current directory:', process.cwd());
console.log('Resolving cryptoUtils from test context:');
try {
  const resolved = require.resolve('./server/utils/cryptoUtils', { paths: [process.cwd()] });
  console.log('Resolved path:', resolved);
  const cryptoUtils = require(resolved);
  console.log('Exports:', Object.keys(cryptoUtils));
} catch (e) {
  console.error('Error:', e.message);
}
