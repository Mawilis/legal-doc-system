import fs from 'fs';
import path from 'path';

function fixRedisImports(dir) {
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
          fixRedisImports(fullPath);
        }
      } else if (stat.isFile() && (fullPath.endsWith('.js') || fullPath.endsWith('.mjs'))) {
        let content = fs.readFileSync(fullPath, 'utf8');
        
        // Match standard default imports for Redis
        const importRegex = /import\s+([a-zA-Z0-9_]+)\s+from\s+['"]([^'"]*config\/redis(?:\.js)?)['"];?/g;
        
        if (importRegex.test(content)) {
          content = content.replace(importRegex, "import * as $1_ns from '$2';\nconst $1 = $1_ns.default || $1_ns.redisClient || $1_ns.client || $1_ns;");
          fs.writeFileSync(fullPath, content);
          console.log(`✅ Patched strict Redis import in: ${fullPath}`);
        }
      }
    } catch (error) {
      // 🛡️ Bulletproof shield
    }
  }
}

console.log("🔍 Scanning for strict Redis default imports with Forensic Shielding...");
fixRedisImports(process.cwd());
console.log("🎯 Redis import cleanup complete.");
