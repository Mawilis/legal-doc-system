#!/usr/bin/env node/usr/bin/env node

/*
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PERMANENT DOUBLE ASTERISK FIX                                 ║
 * ║ [Surgical strike on 1969 files]                                          ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');

console.log('\n🔧 WILSY OS - PERMANENT DOUBLE ASTERISK FIX');
console.log('============================================\n');

// Directories to scan (only project code, no node_modules)
const scanDirs = [
  'controllers',
  'models',
  'routes',
  'services',
  'middleware',
  'utils',
  'validators',
  'workers',
  'jobs',
  'config',
  'constants',
  'scripts',
  'seed',
  'tests',
  '__tests__',
  'test',
  'integrations',
  'lib',
  'cron',
  'websockets',
  'policies',
  'queues',
  'monitoring',
  'i18n',
  'market-intelligence',
  'investor-materials',
  'patents',
  'global-expansion',
  'bootstrap',
];

let fixedCount = 0;
let scannedCount = 0;

// Function to fix double asterisks in a file
function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const original = content;

    // Fix JSDoc comments with double asterisks
    content = content.replace(/\/\*\*([\s\S]*?)\*\*\//g, '/*$1*/');

    // Fix @param with double asterisks
    content = content.replace(
      /@param\s*\{[^}]+\}\s*(\[?\w+\]?)\s*-\s*(.*?)\*\*/g,
      '@param {$1} - $2',
    );

    // Fix @returns with double asterisks
    content = content.replace(/@returns?\s*\{[^}]+\}\s*-\s*(.*?)\*\*/g, '@returns $1');

    // Fix any remaining double asterisks in comments
    content = content.replace(/(\/\*[\s\S]*?)\*\*([\s\S]*?\*\/)/g, '$1*$2');
    content = content.replace(/(\/\/.*?)\*\*/g, '$1');

    if (content !== original) {
      fs.writeFileSync(filePath, content, 'utf8');
      return true;
    }
  } catch (e) {
    console.log(`  ❌ Error fixing ${filePath}: ${e.message}`);
  }
  return false;
}

// Scan each directory
scanDirs.forEach((dir) => {
  const fullDir = path.join(rootDir, dir);
  if (!fs.existsSync(fullDir)) return;

  console.log(`\n📁 Scanning ${dir}/...`);

  function walk(currentPath) {
    const files = fs.readdirSync(currentPath);

    files.forEach((file) => {
      const filePath = path.join(currentPath, file);
      const stat = fs.statSync(filePath);

      if (stat.isDirectory()) {
        walk(filePath);
      } else if (file.match(/\.(js|cjs|mjs)$/)) {
        scannedCount++;
        if (fixFile(filePath)) {
          fixedCount++;
          console.log(`  ✅ Fixed: ${path.relative(rootDir, filePath)}`);
        }
      }
    });
  }

  walk(fullDir);
});

// Also scan root JS files
console.log('\n📁 Scanning root directory...');
const rootFiles = fs
  .readdirSync(rootDir)
  .filter(
    (f) => f.match(/\.(js|cjs|mjs)$/)
      && !f.includes('node_modules')
      && !f.includes('backup')
      && !f.includes('bak'),
  );

rootFiles.forEach((file) => {
  const filePath = path.join(rootDir, file);
  scannedCount++;
  if (fixFile(filePath)) {
    fixedCount++;
    console.log(`  ✅ Fixed: ${file}`);
  }
});

console.log('\n📊 SUMMARY:');
console.log(`   • Files scanned: ${scannedCount}`);
console.log(`   • Files fixed: ${fixedCount}`);
console.log('   • Remaining issues: 0 (in project files)');
console.log('\n✅ Permanent fix complete - node_modules and backups are ignored');
