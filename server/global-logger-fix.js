import fs from 'fs';
import path from 'path';

function fixLogger(dir) {
  let files;
  try {
    files = fs.readdirSync(dir);
  } catch (e) { return; }

  for (const file of files) {
    const fullPath = path.join(dir, file);
    try {
      const stat = fs.lstatSync(fullPath);
      if (stat.isDirectory()) {
        if (!fullPath.includes('node_modules') && !fullPath.includes('.git') && !fullPath.includes('backups')) {
          fixLogger(fullPath);
        }
      } else if (stat.isFile() && (fullPath.endsWith('.js') || fullPath.endsWith('.mjs'))) {
        let content = fs.readFileSync(fullPath, 'utf8');
        let patched = false;

        // Unwrap ESM import
        if (/import\s+logger\s+from/.test(content)) {
          content = content.replace(/import\s+logger\s+from\s+['"]([^'"]+)['"];?/g, "import loggerRaw from '$1';\nconst logger = loggerRaw.default || loggerRaw;");
          patched = true;
        }

        // Unwrap legacy require() import (only if not already patched)
        if (/(?:const|let|var)\s+logger\s*=\s*require/.test(content) && !content.includes('loggerRaw')) {
          content = content.replace(/(?:const|let|var)\s+logger\s*=\s*require\(['"]([^'"]+)['"]\);?/g, "const loggerRaw = require('$1');\nconst logger = loggerRaw.default || loggerRaw;");
          patched = true;
        }

        if (patched) {
          fs.writeFileSync(fullPath, content);
          console.log(`✅ Unwrapped logger in: ${fullPath.split('legal-doc-system/')[1] || fullPath}`);
        }
      }
    } catch (error) {
      // 🛡️ Bulletproof shield
    }
  }
}

console.log("🔍 Scanning codebase to unwrap logger objects...");
fixLogger(process.cwd());
console.log("🎯 Global logger fix complete.");
