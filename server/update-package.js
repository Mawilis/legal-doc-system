#!/usr/bin/env node

/*
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ PACKAGE.JSON UPDATER - WILSY OS FORENSIC ENGINE                          ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const packagePath = path.join(__dirname, 'package.json');

try {
  // Read package.json
  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

  // Add Prettier scripts
  packageJson.scripts = packageJson.scripts || {};
  packageJson.scripts.format = 'prettier --write .';
  packageJson.scripts['format:check'] = 'prettier --check .';
  packageJson.scripts['format:staged'] = 'pretty-quick --staged';
  packageJson.scripts['format:js'] = 'prettier --write "*/*.{js,cjs,mjs}"';
  packageJson.scripts['format:json'] = 'prettier --write "*/*.json"';
  packageJson.scripts['format:fix'] = 'npm run format && npm run lint:fix';

  // Add lint-staged configuration
  packageJson['lint-staged'] = {
    '*.{js,cjs,mjs}': ['prettier --write', 'eslint --fix'],
    '*.{json,md,yml,yaml}': ['prettier --write'],
  };

  // Ensure Prettier is in devDependencies
  packageJson.devDependencies = packageJson.devDependencies || {};
  packageJson.devDependencies.prettier = '^3.1.0';
  packageJson.devDependencies['pretty-quick'] = '^3.1.0';
  packageJson.devDependencies['lint-staged'] = '^15.2.0';
  packageJson.devDependencies['eslint-config-prettier'] = '^9.1.0';

  // Write back
  fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2));

  console.log('✅ package.json updated successfully');
  console.log('\n📋 Added scripts:');
  console.log('   • format - Format all files');
  console.log('   • format:check - Check formatting');
  console.log('   • format:staged - Format staged files');
  console.log('   • format:js - Format JS files only');
  console.log('   • format:fix - Format and lint fix');
} catch (error) {
  console.error('❌ Error updating package.json:', error.message);
  process.exit(1);
}
