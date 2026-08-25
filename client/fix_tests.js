const fs = require('fs');
const path = require('path');

const filesToFix = [
  'tests/client/Reports.test.jsx',
  'client/tests/client/Reports.test.jsx',
  'tests/client/Sovereign_Components.Suite.test.jsx',
  'client/tests/client/Sovereign_Components.Suite.test.jsx',
  'tests/client/templatePage.test.jsx',
  'client/tests/client/templatePage.test.jsx',
  'tests/client/useTenantManagement.test.js',
  'client/tests/client/useTenantManagement.test.js'
];

filesToFix.forEach(relPath => {
  const fullPath = path.resolve(process.cwd(), relPath);
  if (!fs.existsSync(fullPath)) return;

  let content = fs.readFileSync(fullPath, 'utf8');

  // 1. Remove complete multi-line & single-line imports referencing deleted files
  content = content.replace(/import\s*\{[\s\S]*?\}\s*from\s*['"].*?(superadmin|Sovereign_Crisis_Command|Sovereign_Client_Covenant).*?['"];?/g, '');
  content = content.replace(/import\s+.*?from\s*['"].*?(superadmin|Sovereign_Crisis_Command|Sovereign_Client_Covenant).*?['"];?/g, '');
  content = content.replace(/import\s*['"].*?(superadmin|Sovereign_Crisis_Command|Sovereign_Client_Covenant).*?['"];?/g, '');

  // 2. Strip leftover orphaned import braces or dangling syntax near top of file
  const lines = content.split('\n');
  const cleanedLines = [];
  let skippingOrphan = false;

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();

    if (trimmed === 'import {' || (trimmed.startsWith('import') && trimmed.endsWith('{'))) {
      skippingOrphan = true;
      continue;
    }
    if (skippingOrphan) {
      if (trimmed.includes('from') || trimmed.endsWith(';') || trimmed === '}') {
        skippingOrphan = false;
      }
      continue;
    }

    // Drop stray closing braces left at top of file
    if ((trimmed === '}' || trimmed === '};' || trimmed === '}') && i < 25) {
      const prevNonEmpty = cleanedLines.filter(l => l.trim().length > 0);
      if (prevNonEmpty.length === 0 || prevNonEmpty[prevNonEmpty.length - 1].trim().startsWith('import')) {
        continue;
      }
    }

    cleanedLines.push(lines[i]);
  }

  fs.writeFileSync(fullPath, cleanedLines.join('\n'), 'utf8');
  console.log('✓ Repaired & purified syntax in:', relPath);
});
