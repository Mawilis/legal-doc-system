/* eslint-disable */
/*╔════════════════════════════════════════════════════════════════╗
  ║ cryptoUtils.js - FORTUNE 500 CRYPTO UTILITIES                 ║
  ║ [NSA Suite B | FIPS 140-2 | POPIA §19 Compliant]              ║
  ╚════════════════════════════════════════════════════════════════╝*/

import crypto from 'crypto';

// Hashing functions
export const generateHash = (data, prefixed = true) => {
  try {
    const input = typeof data === 'object' ? JSON.stringify(data) : String(data);
    const hash = crypto.createHash('sha256').update(input).digest('hex');
    return prefixed ? `hash:${hash}` : hash;
  } catch (error) {
    console.error('Hash generation failed:', error);
    return `hash:error-${Date.now()}`;
  }
};

export const generateHmac = (data, key) => {
  try {
    const input = typeof data === 'object' ? JSON.stringify(data) : String(data);
    const hmac = crypto.createHmac('sha384', key).update(input).digest('hex');
    return `hmac:${hmac}`;
  } catch (error) {
    console.error('HMAC generation failed:', error);
    return `hmac:error-${Date.now()}`;
  }
};

export const randomBytes = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

export const generateUUID = () => {
  return crypto.randomUUID();
};

// Secure comparison (timing attack safe)
export const secureCompare = (a, b) => {
  try {
    if (typeof a !== 'string' || typeof b !== 'string') return false;
    return crypto.timingSafeEqual(
      Buffer.from(a.padEnd(64, '\0')),
      Buffer.from(b.padEnd(64, '\0'))
    );
  } catch (error) {
    return false;
  }
};

// Merkle tree functions
export const createMerkleProof = (hashes, targetHash) => {
  const proof = [];
  let index = hashes.indexOf(targetHash);
  
  if (index === -1) return null;
  
  let level = [...hashes];
  let levelIndex = index;
  
  while (level.length > 1) {
    const nextLevel = [];
    const isLeft = levelIndex % 2 === 0;
    const siblingIndex = isLeft ? levelIndex + 1 : levelIndex - 1;
    
    if (siblingIndex < level.length) {
      proof.push({
        position: isLeft ? 'right' : 'left',
        hash: level[siblingIndex]
      });
    }
    
    for (let i = 0; i < level.length; i += 2) {
      if (i + 1 < level.length) {
        const combined = level[i] + level[i + 1];
        nextLevel.push(generateHash(combined, false));
      } else {
        nextLevel.push(level[i]);
      }
    }
    
    level = nextLevel;
    levelIndex = Math.floor(levelIndex / 2);
  }
  
  return {
    targetHash,
    proof,
    root: level[0]
  };
};

export const verifyMerkleProof = (targetHash, proof, root) => {
  let hash = targetHash;
  
  for (const step of proof) {
    if (step.position === 'left') {
      hash = generateHash(step.hash + hash, false);
    } else {
      hash = generateHash(hash + step.hash, false);
    }
  }
  
  return hash === root;
};

// Encryption/Decryption
export const encrypt = (data, key) => {
  try {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(key, 'hex'), iv);
    const encrypted = Buffer.concat([cipher.update(JSON.stringify(data), 'utf8'), cipher.final()]);
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted: encrypted.toString('hex'),
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  } catch (error) {
    throw new Error(`Encryption failed: ${error.message}`);
  }
};

export const decrypt = (encryptedData, key) => {
  try {
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      Buffer.from(key, 'hex'),
      Buffer.from(encryptedData.iv, 'hex')
    );
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(encryptedData.encrypted, 'hex')),
      decipher.final()
    ]);
    return JSON.parse(decrypted.toString('utf8'));
  } catch (error) {
    throw new Error(`Decryption failed: ${error.message}`);
  }
};

// Key generation
export const generateKeyPair = () => {
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ec', {
    namedCurve: 'secp384r1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  return { publicKey, privateKey };
};

// Sign/Verify
export const sign = (data, privateKey) => {
  const signer = crypto.createSign('sha384');
  signer.update(JSON.stringify(data));
  signer.end();
  return signer.sign(privateKey, 'hex');
};

export const verify = (data, signature, publicKey) => {
  const verifier = crypto.createVerify('sha384');
  verifier.update(JSON.stringify(data));
  verifier.end();
  return verifier.verify(publicKey, signature, 'hex');
};

// Default export
export default {
  generateHash,
  generateHmac,
  randomBytes,
  generateUUID,
  secureCompare,
  createMerkleProof,
  verifyMerkleProof,
  encrypt,
  decrypt,
  generateKeyPair,
  sign,
  verify
};
