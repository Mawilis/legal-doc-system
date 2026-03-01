#!import fs from 'fs';

const filePath = '/Users/wilsonkhanyezi/legal-doc-system/server/config/redis.js';

try {
  let content = fs.readFileSync(filePath, 'utf8');

  // Only inject if it doesn't already exist
  if (!content.includes('createRequire')) {
    const polyfill =
      "import { createRequire } from 'module';\nconst require = createRequire(import.meta.url);\n";
    fs.writeFileSync(filePath, polyfill + content);
    console.log('✅ Injected ESM require() polyfill into config/redis.js');
  } else {
    console.log('✅ Polyfill already present.');
  }
} catch (error) {
  console.log('⚠️ Could not patch file:', error.message);
}
