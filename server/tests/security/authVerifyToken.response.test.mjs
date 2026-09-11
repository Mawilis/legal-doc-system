import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';

test('verify-token response does not echo submitted credentials', async () => {
  const source = await readFile('server/routes/auth.js', 'utf8');
  assert.doesNotMatch(source, /token:\s*token\s*\|\|\s*null/u);
});

test('verify-token response uses a bounded user projection', async () => {
  const source = await readFile('server/routes/auth.js', 'utf8');
  assert.doesNotMatch(source, /user:\s*req\.user/u);
});
