#!import fs from 'fs';

const redisPath = '/Users/wilsonkhanyezi/legal-doc-system/server/config/redis.js';

try {
  let content = fs.readFileSync(redisPath, 'utf8');

  // Unwrap an ESM import
  content = content.replace(
    /import\s+logger\s+from\s+['"]([^'"]+)['"];?/g,
    "import loggerRaw from '$1';\nconst logger = loggerRaw.default || loggerRaw;",
  );

  // Unwrap a polyfilled require() just in case it's still using that format
  content = content.replace(
    /(?:const|let|var)\s+logger\s*=\s*require\(['"]([^'"]+)['"]\);?/g,
    "const loggerRaw = require('$1');\nconst logger = loggerRaw.default || loggerRaw;",
  );

  fs.writeFileSync(redisPath, content);
  console.log('✅ Successfully unwrapped the logger object in config/redis.js');
} catch (error) {
  console.error('⚠️ Patch failed:', error.message);
}
