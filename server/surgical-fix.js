#!/usr/bin/env node/usr/bin/env node

/*
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SURGICAL FIX ENGINE v1.0                                       ║
 * ║ [Precision fix for corrupted node_modules]                               ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔧 WILSY OS - SURGICAL FIX ENGINE');
console.log('==================================');

const filesToFix = [
  'node_modules/is-callable/index.js',
  'node_modules/es-to-primitive/es2015.js',
  'node_modules/es-to-primitive/es5.js',
  'node_modules/es-to-primitive/es6.js',
  'node_modules/has-symbols/index.js',
];

filesToFix.forEach((filePath) => {
  const fullPath = path.join(__dirname, filePath);

  if (fs.existsSync(fullPath)) {
    try {
      let content = fs.readFileSync(fullPath, 'utf8');
      const original = content;

      // Fix corrupted comments
      content = content.replace(/\/\*\/\s*([\n\r])/g, '/* */$1');
      content = content.replace(
        /\}\s+catch\s*\(\s*e\s*\)\s*\{\s*\/\*\/\s*\}/g,
        '} catch (e) { /* ignore */ }'
      );
      content = content.replace(/\/\*\/\s*\}/g, '/* */ }');

      // Fix any remaining double asterisks in comments
      content = content.replace(/(\/\*[\s\S]*?)\*\*([\s\S]*?\*\/)/g, '$1*$2');

      if (content !== original) {
        fs.writeFileSync(fullPath, content);
        console.log(`✅ Fixed: ${filePath}`);
      } else {
        console.log(`✓ Already clean: ${filePath}`);
      }
    } catch (e) {
      console.log(`⚠️ Could not fix ${filePath}: ${e.message}`);
    }
  }
});

console.log('\n✅ Surgical fix complete');
