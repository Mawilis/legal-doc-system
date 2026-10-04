
import {
  describe,
  expect,
  it,
} from 'vitest';

import {
  generateHash,
  generateHmac,
  randomBytes,
  generateUUID,
  secureCompare,
  encrypt,
  decrypt,
  generateKeyPair,
  sign,
  verify,
  createMerkleProof,
  verifyMerkleProof,
} from './cryptoUtils.js';

describe(
  'cryptoUtils Web Crypto migration contract',
  () => {
    it(
      'preserves SHA-256 and HMAC contracts',
      async () => {
        expect(
          await generateHash(
            'wilsy',
            false,
          ),
        ).toMatch(
          /^[0-9a-f]{64}$/,
        );

        expect(
          await generateHmac(
            'payload',
            'secret',
          ),
        ).toMatch(
          /^hmac:[0-9a-f]{96}$/,
        );
      },
    );

    it(
      'preserves random and UUID contracts',
      () => {
        expect(
          randomBytes(32),
        ).toMatch(
          /^[0-9a-f]{64}$/,
        );

        expect(
          generateUUID(),
        ).toMatch(
          /^[0-9a-f-]{36}$/i,
        );
      },
    );

    it(
      'preserves comparison behavior',
      () => {
        expect(
          secureCompare(
            'same',
            'same',
          ),
        ).toBe(true);

        expect(
          secureCompare(
            'same',
            'different',
          ),
        ).toBe(false);
      },
    );

    it(
      'round trips AES-256-GCM',
      async () => {
        const key =
          randomBytes(32);

        const sealed =
          await encrypt(
            { value: 42 },
            key,
          );

        await expect(
          decrypt(
            sealed,
            key,
          ),
        ).resolves.toEqual(
          { value: 42 },
        );
      },
    );

    it(
      'generates P-384 PEM and signs/verifies',
      async () => {
        const keys =
          await generateKeyPair();

        expect(
          keys.publicKey,
        ).toContain(
          'BEGIN PUBLIC KEY',
        );

        expect(
          keys.privateKey,
        ).toContain(
          'BEGIN PRIVATE KEY',
        );

        const payload = {
          tenant: 'cert',
          amount: 1,
        };

        const signature =
          await sign(
            payload,
            keys.privateKey,
          );

        await expect(
          verify(
            payload,
            signature,
            keys.publicKey,
          ),
        ).resolves.toBe(true);
      },
    );

    it(
      'preserves Merkle proof semantics',
      async () => {
        const leaves = await Promise.all(
          ['a','b','c','d'].map(
            value =>
              generateHash(
                value,
                false,
              ),
          ),
        );

        const proof =
          await createMerkleProof(
            leaves,
            leaves[1],
          );

        expect(
          verifyMerkleProof(
            proof.targetHash,
            proof.proof,
            proof.root,
          ),
        ).toBe(true);
      },
    );
  },
);
