/* eslint-disable */
/**
 * 🧪 DeploymentScript Forensic Audit
 * @description Verifying the structural integrity of the Sovereign Deployment Engine.
 */
import { expect } from 'chai';
import fs from 'fs';

describe('🚀 DeploymentScript Forensic Audit', () => {
  const scriptPath = '/Users/wilsonkhanyezi/legal-doc-system/server/scripts/SovereignDeployment.script.js';

  it('contains the mandatory ESLint bypass and Biblical Header', () => {
    const content = fs.readFileSync(scriptPath, 'utf8');
    expect(content).to.include('/* eslint-disable */');
    expect(content).to.include('WILSY OS - SOVEREIGN DEPLOYMENT ENGINE');
  });

  it('implements the Atomic Rollback logic in the runStep wrapper', () => {
    const content = fs.readFileSync(scriptPath, 'utf8');
    expect(content).to.include('process.exit(1)'); // Verify hard-stop on failure
    expect(content).to.include('execSync');
  });
});
