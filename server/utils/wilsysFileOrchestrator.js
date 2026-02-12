const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
class WilsyFileOrchestrator {
  constructor() { this.version = '1.0.0'; this.writtenFiles = new Map(); this.auditLog = []; }
  atomicWrite(filePath, content) {
    const absolutePath = filePath.startsWith('/') ? filePath : path.join('/Users/wilsonkhanyezi/legal-doc-system/server', filePath);
    const dir = path.dirname(absolutePath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const tempPath = `${absolutePath}.tmp.${Date.now()}`;
    fs.writeFileSync(tempPath, content, 'utf8');
    const written = fs.readFileSync(tempPath, 'utf8');
    if (written.length !== content.length) throw new Error(`INTEGRITY FAILURE: ${filePath} - truncation`);
    const hash = crypto.createHash('sha256').update(content).digest('hex');
    fs.renameSync(tempPath, absolutePath);
    const final = fs.readFileSync(absolutePath, 'utf8');
    if (crypto.createHash('sha256').update(final).digest('hex') !== hash) throw new Error(`VERIFICATION FAILURE: ${filePath} - hash mismatch`);
    this.writtenFiles.set(absolutePath, { path: absolutePath, size: content.length, hash, timestamp: new Date().toISOString() });
    this.auditLog.push({ operation: 'ATOMIC_WRITE', path: absolutePath, size: content.length, hash, timestamp: new Date().toISOString() });
    console.log(`  ✓ ATOMIC: ${path.basename(absolutePath)} (${content.length} bytes) [${hash.substring(0,8)}]`);
    return { path: absolutePath, size: content.length, hash, verified: true };
  }
  batchDeploy(files) { const r=[],e=[]; for(const [p,c] of Object.entries(files)) { try { r.push(this.atomicWrite(p,c)); } catch(err) { e.push({file:p,error:err.message}); } } return { success: e.length===0, deployed: r.length, failed: e.length, results: r, errors: e, timestamp: new Date().toISOString() }; }
  verifyIntegrity() {
    const v=[];
    for(const [fp,rec] of this.writtenFiles) {
      try {
        if (!fs.existsSync(fp)) { v.push({ path: fp, exists: false, integrity: 'FAILED - MISSING' }); continue; }
        const content = fs.readFileSync(fp, 'utf8');
        const hash = crypto.createHash('sha256').update(content).digest('hex');
        v.push({ path: fp, exists: true, size: content.length, expectedSize: rec.size, hash, expectedHash: rec.hash, integrity: hash===rec.hash ? 'PASSED' : 'FAILED - HASH MISMATCH', timestamp: new Date().toISOString() });
      } catch(err) { v.push({ path: fp, error: err.message, integrity: 'FAILED - READ ERROR' }); }
    }
    return v;
  }
  generateDeploymentEvidence() {
    const evidence = {
      orchestrator: { version: this.version, timestamp: new Date().toISOString(), nodeVersion: process.version },
      deployment: { totalFiles: this.writtenFiles.size, files: Array.from(this.writtenFiles.values()), auditLog: this.auditLog },
      integrity: this.verifyIntegrity(),
      forensicHash: crypto.createHash('sha256').update(JSON.stringify(this.auditLog)).digest('hex')
    };
    this.atomicWrite('/Users/wilsonkhanyezi/legal-doc-system/server/deployment-evidence.json', JSON.stringify(evidence, null, 2));
    return evidence;
  }
}
module.exports = new WilsyFileOrchestrator();
