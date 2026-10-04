
import {
  describe,
  expect,
  it,
} from 'vitest';

import CryptoJS from 'crypto-js';
import { sha3_512 } from 'js-sha3';

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
  'hybrid crypto migration',
  () => {
    it(
      'keeps SHA-256 synchronous',
      () => {
        const result =
          generateHash(
            'wilsy',
            false,
          );

        expect(
          result instanceof Promise,
        ).toBe(false);

        expect(result).toBe(
          CryptoJS
            .SHA256('wilsy')
            .toString(
              CryptoJS.enc.Hex,
            ),
        );
      },
    );

    it(
      'keeps HMAC-SHA384 synchronous',
      () => {
        const result =
          generateHmac(
            'payload',
            'secret',
          );

        expect(
          result instanceof Promise,
        ).toBe(false);

        expect(result).toBe(
          'hmac:' +
          CryptoJS
            .HmacSHA384(
              'payload',
              'secret',
            )
            .toString(
              CryptoJS.enc.Hex,
            ),
        );
      },
    );

    it(
      'keeps randomness and UUID synchronous',
      () => {
        const bytes =
          randomBytes(32);

        expect(
          bytes instanceof Promise,
        ).toBe(false);

        expect(bytes).toMatch(
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
      'keeps secure comparison synchronous',
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
      'keeps Merkle operations synchronous',
      () => {
        const leaves = [
          'a',
          'b',
          'c',
          'd',
        ].map(
          value =>
            generateHash(
              value,
              false,
            ),
        );

        const proof =
          createMerkleProof(
            leaves,
            leaves[1],
          );

        expect(
          proof instanceof Promise,
        ).toBe(false);

        expect(
          verifyMerkleProof(
            proof.targetHash,
            proof.proof,
            proof.root,
          ),
        ).toBe(true);
      },
    );

    it(
      'uses Web Crypto asynchronously for AES-GCM',
      async () => {
        const key =
          randomBytes(32);

        const encrypted =
          await encrypt(
            { value: 42 },
            key,
          );

        await expect(
          decrypt(
            encrypted,
            key,
          ),
        ).resolves.toEqual(
          { value: 42 },
        );
      },
    );

    it(
      'uses Web Crypto P-384 signing',
      async () => {
        const pair =
          await generateKeyPair();

        const data = {
          tenant: 'cert',
          amount: 42,
        };

        const signature =
          await sign(
            data,
            pair.privateKey,
          );

        await expect(
          verify(
            data,
            signature,
            pair.publicKey,
          ),
        ).resolves.toBe(true);
      },
    );

    it(
      'retains exact js-sha3 synchronous semantics',
      () => {
        const input =
          JSON.stringify({
            tenant: 'cert',
            amount: 42,
          });

        const digest =
          sha3_512(input);

        expect(
          digest instanceof Promise,
        ).toBe(false);

        expect(digest).toMatch(
          /^[0-9a-f]{128}$/,
        );
      },
    );
  },
);
