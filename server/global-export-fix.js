#!import fs from 'fs';
import path from 'path';

function fixExports(dir) {
  let files;
  try {
    files = fs.readdirSync(dir);
  } catch (e) {
    return;
  }

  for (const file of files) {
    const fullPath = path.join(dir, file);
    try {
      const stat = fs.lstatSync(fullPath);

      if (stat.isDirectory()) {
        if (
          !fullPath.includes('node_modules')
          && !fullPath.includes('.git')
          && !fullPath.includes('backups')
        ) {
          fixExports(fullPath);
        }
      } else if (stat.isFile() && (fullPath.endsWith('.js') || fullPath.endsWith('.mjs'))) {
        let content = fs.readFileSync(fullPath, 'utf8');

        if (content.includes('module.exports')) {
          // Upgrade legacy exports to ESM default exports
          content = content.replace(/module\.exports\s*=\s*/g, 'export default ');
          fs.writeFileSync(fullPath, content);
          console.log(
            `✅ Upgraded export in: ${fullPath.split('legal-doc-system/')[1] || fullPath}`,
          );
        }
      }
    } catch (error) {
      // 🛡️ Bulletproof shield
    }
  }
}

console.log('🔍 Scanning codebase for legacy module.exports...');
fixExports(process.cwd());
console.log('🎯 Global export upgrade complete.');
