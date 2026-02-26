#!/usr/bin/env node

/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FINAL DOUBLE ASTERISK FIX                                     ║
 * ║ [Surgical strike on the last 8 files]                                    ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');

console.log('\n🔧 WILSY OS - FINAL DOUBLE ASTERISK FIX');
console.log('========================================\n');

// The 8 files that still have issues
const filesToFix = [
  'middleware/asyncHandler.js',
  'models/caseFileModel.js',
  'models/KYCVerification.js',
  'scripts/migrate-documents-tenancy.js',
  'scripts/fix-double-asterisks-permanent.js',
  'controllers/popiaController.js',
  'routes/legal/index.js',
  'services/storageService.js',
];

let fixedCount = 0;

filesToFix.forEach((relativePath) => {
  const fullPath = path.join(rootDir, relativePath);

  if (!fs.existsSync(fullPath)) {
    console.log(`⚠️  File not found: ${relativePath}`);
    return;
  }

  try {
    let content = fs.readFileSync(fullPath, 'utf8');
    const original = content;

    // Fix 1: JSDoc comments with double asterisks
    content = content.replace(/\/\*\*([\s\S]*?)\*\*\//g, '/*$1*/');

    // Fix 2: @param with double asterisks
    content = content.replace(/@param\s*\{[^}]+\}\s*(\[?\w+\]?)\s*-\s*(.*?)\*\*/g, '@param {$1} - $2');

    // Fix 3: @returns with double asterisks
    content = content.replace(/@returns?\s*\{[^}]+\}\s*-\s*(.*?)\*\*/g, '@returns $1');

    // Fix 4: Any remaining double asterisks in comments
    content = content.replace(/(\/\*[\s\S]*?)\*\*([\s\S]*?\*\/)/g, '$1*$2');
    content = content.replace(/(\/\/.*?)\*\*/g, '$1');

    // Fix 5: Specific pattern for asyncHandler.js
    content = content.replace(/catch\s*\(\s*error\s*\)\s*\{\s*\/\*\/\s*\}/g, 'catch (error) { /* ignore */ }');

    // Fix 6: Specific pattern for caseFileModel.js
    content = content.replace(/\/\*\*[\s\S]*?@description[\s\S]*?\*\*\//g, (match) => match.replace(/\*\*/g, '*'));

    if (content !== original) {
      fs.writeFileSync(fullPath, content, 'utf8');
      console.log(`✅ Fixed: ${relativePath}`);
      fixedCount++;
    } else {
      console.log(`✓ Already clean: ${relativePath}`);
    }
  } catch (e) {
    console.log(`❌ Error fixing ${relativePath}: ${e.message}`);
  }
});

console.log('\n📊 SUMMARY:');
console.log(`   • Files attempted: ${filesToFix.length}`);
console.log(`   • Files fixed: ${fixedCount}`);
console.log(`   • Remaining issues: ${filesToFix.length - fixedCount}`);

// Now verify
console.log('\n🔍 VERIFYING...');
const verifyCmd = 'find . -type f \\( -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \\) \
  -not -path "*/node_modules/*" \
  -not -path "*/coverage/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.git/*" \
  -not -name "*.bak" \
  -not -name "*.backup*" \
  -not -path "*/tests_legacy_backup/*" 2>/dev/null | xargs grep -l "\\*\\*" 2>/dev/null | wc -l';

const { execSync } = await import('child_process');
const remaining = parseInt(execSync(verifyCmd, { encoding: 'utf8' }).trim()) || 0;

console.log(`   • Project files with double asterisks: ${remaining} (should be 0)`);

if (remaining === 0) {
  console.log('\n✅ ALL PROJECT FILES ARE CLEAN!');
} else {
  console.log('\n⚠️  Some files still have issues. Run again or check manually.');
}
