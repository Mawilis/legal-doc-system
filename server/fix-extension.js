#!import fs from 'fs';

const redisPath = '/Users/wilsonkhanyezi/legal-doc-system/server/config/redis.js';

try {
  let content = fs.readFileSync(redisPath, 'utf8');

  // Find the metrics import and enforce the .js extension
  content = content.replace(/from\s+['"]([^'"]+?\/metrics)['"]/g, "from '$1.js'");

  // Clean up any double extensions just in case (e.g. metrics.js.js)
  content = content.replace(/\.js\.js/g, '.js');

  fs.writeFileSync(redisPath, content);
  console.log('✅ Fixed ESM file extension requirement in config/redis.js');
} catch (error) {
  console.error('⚠️ Patch failed:', error.message);
}
