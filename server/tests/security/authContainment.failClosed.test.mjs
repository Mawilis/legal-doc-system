import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';

const surfaces = ['server/middleware/authMiddleware.js', 'server/middleware/auth.middleware.js'];
const executable = (source) => source.replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');

test('authentication middleware has no hard-coded JWT secret fallback', async () => {
  for (const path of surfaces) {
    const source = executable(await readFile(path, 'utf8'));
    assert.doesNotMatch(
      source,
      /['"]wilsy_sovereign_secret['"]/u,
      `${path} contains a default secret`
    );
  }
});

test('authentication middleware does not synthesize privileged identity on lookup failure', async () => {
  for (const path of surfaces) {
    const source = executable(await readFile(path, 'utf8'));
    assert.doesNotMatch(
      source,
      /SIGNED_JWT_DB_LOOKUP_BYPASS|role:\s*decoded|tenantId:\s*decoded|securityClearance:\s*decoded/u,
      `${path} contains claim-derived fallback authority`
    );
  }
});

test('authentication middleware does not derive tenant or role authority from claims', async () => {
  for (const path of surfaces) {
    const source = executable(await readFile(path, 'utf8'));
    assert.doesNotMatch(
      source,
      /req\.user\.tenantId\s*=\s*normalize|decodedRole/u,
      `${path} derives authority from claims`
    );
  }
});

test('authentication middleware has no founder-email continuity bypass', async () => {
  for (const path of surfaces) {
    const source = executable(await readFile(path, 'utf8'));
    assert.doesNotMatch(
      source,
      /founderEmail|FOUNDER_EMAIL|founder.*email/iu,
      `${path} contains founder continuity`
    );
  }
});
