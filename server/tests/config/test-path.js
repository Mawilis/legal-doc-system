const path = require('path');
console.log('Current directory:', process.cwd());
console.log('Resolved config path:', path.resolve('config/security.js'));
try {
  const config = require('../../config/security');
  console.log('✅ Successfully loaded config');
  console.log('Config methods:', Object.keys(config).filter(k => !k.startsWith('_')).join(', '));
} catch (err) {
  console.error('❌ Failed to load config:', err.message);
  console.error(err.stack);
}
