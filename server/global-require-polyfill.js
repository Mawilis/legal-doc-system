import fs from 'fs';
import path from 'path';

function injectRequirePolyfill(dir) {
  let files;
  try {
    files = fs.readdirSync(dir);
  } catch (e) { return; } // Safely skip unreadable directories

  for (const file of files) {
    const fullPath = path.join(dir, file);
    try {
      const stat = fs.lstatSync(fullPath);
      
      if (stat.isDirectory()) {
        // Skip dependencies and backups to keep it fast and safe
        if (!fullPath.includes('node_modules') && !fullPath.includes('.git') && !fullPath.includes('backups')) {
          injectRequirePolyfill(fullPath);
        }
      } else if (stat.isFile() && (fullPath.endsWith('.js') || fullPath.endsWith('.mjs'))) {
        let content = fs.readFileSync(fullPath, 'utf8');
        
        // If the file uses require() but doesn't already have the polyfill...
        if (/\brequire\s*\(/.test(content) && !content.includes('createRequire')) {
          const polyfill = "import { createRequire as _createRequire } from 'module';\nconst require = _createRequire(import.meta.url);\n";
          fs.writeFileSync(fullPath, polyfill + content);
          console.log(`✅ Injected ESM require() polyfill into: ${fullPath.split('legal-doc-system/')[1] || fullPath}`);
        }
      }
    } catch (error) {
      // 🛡️ Bulletproof shield
    }
  }
}

console.log("🔍 Scanning entire codebase for naked require() calls...");
injectRequirePolyfill(process.cwd());
console.log("🎯 Global polyfill injection complete.");
