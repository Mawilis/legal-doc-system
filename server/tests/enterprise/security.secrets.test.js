/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS 2050 - FORENSIC SECRET SCANNER (ANTI-LEAK ENGINE)                ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/
import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Point to the root of the entire legal-doc-system repository
const PROJECT_ROOT = path.resolve(__dirname, '../../../'); 

const EXCLUDED_DIRS = new Set(['node_modules', '.git', 'coverage', 'test-results', 'dist', 'ssl', 'logs']);
const ALLOWED_EXTENSIONS = new Set(['.js', '.yml', '.yaml', '.json', '.env', '.md', '.cjs']);

// The Quantum Signature dictionary of forbidden patterns
const SECRET_PATTERNS = {
  'Private Key Block': /-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----/,
  'AWS Access Key': /(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}/,
  'GitHub Token': /gh[pousr]_[A-Za-z0-9_]{36,255}/,
  'Slack Webhook/Token': /https:\/\/hooks\.slack\.com\/services\/T[a-zA-Z0-9_]{8}\/B[a-zA-Z0-9_]{8}\/[a-zA-Z0-9_]{24}|xox[baprs]-[0-9]{12}-[0-9]{12}/,
  'Hardcoded MongoDB Credentials': /mongodb(?:\+srv)?:\/\/[^:]+:(?!\$\{)[^@]+@/, // Matches mongo URIs unless they use ${VAR} syntax
  'Exposed Admin Password': /${ADMIN_PASSWORD:-REDACTED}/ // Specific catch for your known password
};

// Recursive file gatherer
function getFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  try {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      try {
        const stat = fs.lstatSync(fullPath);
        if (stat.isDirectory()) {
          if (!EXCLUDED_DIRS.has(file)) {
            getFiles(fullPath, fileList);
          }
        } else {
          const ext = path.extname(file);
          if (ALLOWED_EXTENSIONS.has(ext) || file.startsWith('.env') || file === '.gitignore') {
            fileList.push(fullPath);
          }
        }
      } catch (err) { /* Ignore broken symlinks */ }
    }
  } catch (err) { /* Ignore unreadable dirs */ }
  return fileList;
}

describe('🏛️ WILSY OS 2050 - FORENSIC SECRETS LEAK PREVENTION', function() {
  this.timeout(10000); // Allow time for full repo scan
  let filesToScan = [];

  before(() => {
    filesToScan = getFiles(PROJECT_ROOT);
    console.log(`\n  🔍 Scanning ${filesToScan.length} files for cryptographic and credential leaks...`);
  });

  it('[SEC001] SHOULD NOT contain hardcoded secrets, keys, or passwords in the repository', () => {
    const leaks = [];

    for (const file of filesToScan) {
      // Don't scan the test file itself to prevent false positives
      if (file.includes('security.secrets.test.js') || file.includes('.env')) continue;

      let content = '';
      try {
        content = fs.readFileSync(file, 'utf8');
      } catch (err) { continue; }
      
      for (const [secretName, regex] of Object.entries(SECRET_PATTERNS)) {
        if (regex.test(content)) {
          // Provide a relative path for cleaner logs
          const relativePath = file.replace(PROJECT_ROOT, '');
          leaks.push(`[${secretName}] found in ${relativePath}`);
        }
      }
    }

    if (leaks.length > 0) {
      console.error('\n🚨 CRITICAL SECURITY BREACH DETECTED:');
      leaks.forEach(leak => console.error(`   ❌ ${leak}`));
      console.error('Please replace these with process.env or GitHub Secrets (${{ secrets.XYZ }}).\n');
    }

    expect(leaks).to.be.an('array').that.is.empty;
  });

  it('[SEC002] SHOULD have .env explicitly ignored in .gitignore', () => {
    const gitignorePath = path.join(PROJECT_ROOT, '.gitignore');
    const serverGitignorePath = path.join(PROJECT_ROOT, 'server', '.gitignore');
    
    let isIgnored = false;
    
    if (fs.existsSync(gitignorePath)) {
      const content = fs.readFileSync(gitignorePath, 'utf8');
      if (content.includes('.env')) isIgnored = true;
    }
    
    if (fs.existsSync(serverGitignorePath)) {
      const content = fs.readFileSync(serverGitignorePath, 'utf8');
      if (content.includes('.env')) isIgnored = true;
    }

    expect(isIgnored, 'No .env found in .gitignore files').to.be.true;
  });

  it('[SEC003] SHOULD NOT have live .env files tracked in the repository', () => {
    const liveEnvFiles = filesToScan.filter(file => {
      const fileName = path.basename(file);
      // Allow .env.example or .env.test, but block .env or .env.production
      return fileName === '.env' || fileName === '.env.production';
    });

    if (liveEnvFiles.length > 0) {
      console.log('⚠️ Warning: Found live .env files. Ensure they are not committed to Git:');
      liveEnvFiles.forEach(f => console.log(`   - ${f.replace(PROJECT_ROOT, '')}`));
    }
    
    // We don't fail the test here if it's local, but we flag it
    // In CI, .env shouldn't exist unless created dynamically
    if (process.env.GITHUB_ACTIONS) {
      expect(liveEnvFiles.length, 'Live .env files found in CI environment').to.equal(0);
    }
  });
});
