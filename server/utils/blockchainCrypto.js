/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ BLOCKCHAIN CRYPTO UTILITIES - INVESTOR-GRADE MODULE                       ║
  ║ Cryptographic proofs | Merkle trees | Zero-knowledge proofs              ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/blockchainCrypto.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-03-02
 */

import crypto from 'crypto';

// ============================================================================
// HASH FUNCTIONS
// ============================================================================

export const sha256 = (data) => {
  return crypto.createHash('sha256').update(data).digest('hex');
};

export const sha256Buffer = (data) => {
  return crypto.createHash('sha256').update(data).digest();
};

export const doubleSha256 = (data) => {
  const first = crypto.createHash('sha256').update(data).digest();
  return crypto.createHash('sha256').update(first).digest('hex');
};

export const hashObject = (obj) => {
  const canonical = JSON.stringify(obj, Object.keys(obj).sort());
  return sha256(canonical);
};

// ============================================================================
// MERKLE TREE
// ============================================================================

export class MerkleTree {
  constructor(leaves) {
    this.leaves = leaves.map(leaf => sha256Buffer(leaf));
    this.levels = this.buildLevels(this.leaves);
    this.root = this.levels[this.levels.length - 1][0];
  }

  buildLevels(leaves) {
    const levels = [leaves];
    
    while (levels[levels.length - 1].length > 1) {
      const currentLevel = levels[levels.length - 1];
      const nextLevel = [];
      
      for (let i = 0; i < currentLevel.length; i += 2) {
        if (i + 1 < currentLevel.length) {
          const combined = Buffer.concat([currentLevel[i], currentLevel[i + 1]]);
          nextLevel.push(sha256Buffer(combined));
        } else {
          nextLevel.push(currentLevel[i]);
        }
      }
      
      levels.push(nextLevel);
    }
    
    return levels;
  }

  getProof(leaf) {
    const leafHash = sha256Buffer(leaf);
    let index = this.leaves.findIndex(h => h.equals(leafHash));
    
    if (index === -1) {
      throw new Error('Leaf not found in tree');
    }

    const proof = [];
    
    for (let level = 0; level < this.levels.length - 1; level++) {
      const currentLevel = this.levels[level];
      const isRightNode = index % 2 === 1;
      const siblingIndex = isRightNode ? index - 1 : index + 1;

      if (siblingIndex < currentLevel.length) {
        proof.push({
          position: isRightNode ? 'left' : 'right',
          hash: currentLevel[siblingIndex].toString('hex')
        });
      }

      index = Math.floor(index / 2);
    }

    return proof;
  }

  verifyProof(leaf, proof, root) {
    let hash = sha256Buffer(leaf);
    
    for (const node of proof) {
      const siblingHash = Buffer.from(node.hash, 'hex');
      
      if (node.position === 'left') {
        hash = sha256Buffer(Buffer.concat([siblingHash, hash]));
      } else {
        hash = sha256Buffer(Buffer.concat([hash, siblingHash]));
      }
    }
    
    return hash.toString('hex') === root;
  }

  getRoot() {
    return this.levels[this.levels.length - 1][0].toString('hex');
  }
}

// ============================================================================
// DIGITAL SIGNATURES
// ============================================================================

export const generateKeyPair = () => {
  return crypto.generateKeyPairSync('rsa', {
    modulusLength: 4096,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
};

export const signData = (data, privateKey) => {
  const sign = crypto.createSign('SHA256');
  sign.update(data);
  sign.end();
  return sign.sign(privateKey, 'hex');
};

export const verifySignature = (data, signature, publicKey) => {
  const verify = crypto.createVerify('SHA256');
  verify.update(data);
  verify.end();
  return verify.verify(publicKey, signature, 'hex');
};

// ============================================================================
// ZERO-KNOWLEDGE PROOFS (SIMPLIFIED)
// ============================================================================

export class ZKProof {
  static generateCommitment(secret, salt) {
    const combined = secret + (salt || crypto.randomBytes(32).toString('hex'));
    return sha256(combined);
  }

  static generateChallenge(commitment, verifier) {
    return sha256(commitment + verifier).slice(0, 16);
  }

  static generateResponse(secret, challenge, salt) {
    const combined = secret + challenge + salt;
    return sha256(combined);
  }

  static verify(commitment, challenge, response, salt, verifier) {
    const expectedChallenge = sha256(commitment + verifier).slice(0, 16);
    if (expectedChallenge !== challenge) return false;

    const expectedResponse = sha256('secret' + challenge + salt);
    return response === expectedResponse;
  }
}

// ============================================================================
// PROOF OF EXISTENCE
// ============================================================================

export const generateProofOfExistence = (documentHash, timestamp, anchorId) => {
  const proof = {
    version: '1.0',
    documentHash,
    timestamp,
    anchorId,
    merkleRoot: null,
    merkleProof: null
  };

  proof.signature = signData(
    JSON.stringify({ documentHash, timestamp, anchorId }),
    process.env.BLOCKCHAIN_PRIVATE_KEY || 'default-private-key'
  );

  return proof;
};

export const verifyProofOfExistence = (proof, publicKey) => {
  const { documentHash, timestamp, anchorId, signature } = proof;
  return verifySignature(
    JSON.stringify({ documentHash, timestamp, anchorId }),
    signature,
    publicKey
  );
};

// ============================================================================
// CHAIN OF CUSTODY
// ============================================================================

export class ChainOfCustody {
  constructor() {
    this.entries = [];
    this.currentHash = null;
  }

  addEntry(entry) {
    const timestamp = Date.now();
    const previousHash = this.currentHash || '0'.repeat(64);
    
    const entryData = {
      ...entry,
      timestamp,
      previousHash
    };

    const entryHash = sha256(JSON.stringify(entryData));
    this.entries.push({ ...entryData, hash: entryHash });
    this.currentHash = entryHash;

    return entryHash;
  }

  verifyChain() {
    for (let i = 0; i < this.entries.length; i++) {
      const entry = this.entries[i];
      const expectedPreviousHash = i === 0 ? '0'.repeat(64) : this.entries[i - 1].hash;
      
      if (entry.previousHash !== expectedPreviousHash) {
        return { valid: false, brokenAt: i };
      }

      const recomputedHash = sha256(JSON.stringify({
        ...entry,
        hash: undefined
      }));

      if (recomputedHash !== entry.hash) {
        return { valid: false, tamperedAt: i };
      }
    }

    return { valid: true, entries: this.entries.length };
  }

  getProof(index) {
    if (index < 0 || index >= this.entries.length) {
      throw new Error('Index out of range');
    }

    return {
      entry: this.entries[index],
      chain: this.entries.slice(0, index + 1),
      currentHash: this.currentHash
    };
  }
}

export default {
  sha256,
  doubleSha256,
  hashObject,
  MerkleTree,
  generateKeyPair,
  signData,
  verifySignature,
  ZKProof,
  generateProofOfExistence,
  verifyProofOfExistence,
  ChainOfCustody
};
