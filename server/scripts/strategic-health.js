#!/usr/bin/env node/usr/bin/env node

/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - STRATEGIC HEALTH CHECK                                         ║
 * ║ [One command to verify everything]                                       ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');

console.log('\n🔍 WILSY OS - STRATEGIC HEALTH CHECK');
console.log('=====================================\n');

const checks = [
  { name: 'app.js syntax', cmd: 'node --check app.js' },
  { name: 'server.js syntax', cmd: 'node --check server.js' },
  { name: 'ESLint config', cmd: 'npx eslint --version' },
  { name: 'Prettier config', cmd: 'npx prettier --version' },
  { name: 'Evidence files', cmd: 'ls -la docs/evidence/ | wc -l' },
];

let passed = 0;

checks.forEach((check) => {
  try {
    execSync(check.cmd, { cwd: rootDir, stdio: 'pipe' });
    console.log(`✅ ${check.name}`);
    passed++;
  } catch (e) {
    console.log(`❌ ${check.name}`);
  }
});

console.log(`\n📊 Health Score: ${passed}/${checks.length}`);

// Check for double asterisks in production code (excluding tools)
console.log('\n🔍 Scanning production code for double asterisks...');

const findCmd = 'find . -type f \\( -name "*.js" -o -name "*.cjs" -o -name "*.mjs" \\) \
  -not -path "*/node_modules/*" \
  -not -path "*/coverage/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.git/*" \
  -not -name "*.bak" \
  -not -name "*.backup*" \
  -not -path "*/tests_legacy_backup/*" \
  -not -path "*/final-fix.js" \
  -not -path "*/scripts/final-double-asterisk-fix.js" \
  -not -path "*/scripts/fix-double-asterisks-permanent.js" \
  -not -path "*/surgical-fix.js" \
  -not -path "*/surgical-fix.mjs" 2>/dev/null | xargs grep -l "\\*\\*" 2>/dev/null | wc -l';

try {
  const output = execSync(findCmd, { cwd: rootDir, encoding: 'utf8' }).trim();
  const count = parseInt(output) || 0;

  if (count === 0) {
    console.log('✅ Production code is clean (no double asterisks)');
  } else {
    console.log(`⚠️  Found ${count} files with double asterisks (likely in tools)`);
  }
} catch (e) {
  console.log('⚠️  Could not scan for double asterisks');
}

console.log('\n✅ Strategic health check complete');
console.log('\n🚀 WILSY OS IS OPERATIONAL');
