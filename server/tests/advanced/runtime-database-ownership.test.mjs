import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { describe, it } from 'node:test';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');

describe('EOS runtime database ownership inventory', () => {
  it('keeps the active Node BFF database-free and delegates PDF identity to EOS', async () => {
    const source = await readFile(resolve(ROOT, 'server/server.js'), 'utf8');
    assert.doesNotMatch(source, /mongoose/);
    assert.match(source, /database: 'NOT_CONNECTED_BY_BFF'/);
    assert.match(source, /databaseAuthority: 'PYTHON_EOS'/);
    assert.doesNotMatch(source, /MongoClient|MONGODB_URI|MONGO_URI/);

    const pdfController = await readFile(
      resolve(ROOT, 'server/controllers/businessArtifactPdfController.js'),
      'utf8',
    );
    assert.doesNotMatch(pdfController, /mongoose|findWilsyLiveUserProfileDocument/);
    assert.match(pdfController, /EOS_VERIFIED_WORKSPACE_BOOTSTRAP/);
    assert.match(source, /resolveEosWorkspaceIdentity/);
    assert.match(source, /requireEosWorkspaceIdentity, generateSovereignArtifactPdf/);

    const identityAdapter = await readFile(
      resolve(ROOT, 'server/services/eosWorkspaceIdentity.js'),
      'utf8',
    );
    assert.match(identityAdapter, /\/api\/auth\/workspace-bootstrap/);
  });

  it('keeps PM2 and local development on the repository-defined EOS entrypoints', async () => {
    const pm2 = await readFile(resolve(ROOT, 'server/ecosystem.config.js'), 'utf8');
    assert.match(pm2, /script: '\.\/server\.js'/);
    assert.doesNotMatch(pm2, /app\.js|scheduler\.js/);

    const dev = await readFile(resolve(ROOT, 'scripts/start-dev-stack.sh'), 'utf8');
    assert.match(dev, /uvicorn tools\.eos\.api\.server:app/);
    assert.doesNotMatch(dev, /server\/app\.js|server\/jobs\/scheduler\.js/);

    const packageJson = JSON.parse(await readFile(resolve(ROOT, 'package.json'), 'utf8'));
    assert.equal(packageJson.scripts.dev, 'bash scripts/start-dev-stack.sh');
    assert.match(packageJson.scripts['dev:kernel'], /uvicorn tools\.eos\.api\.server:app/);
  });
});
