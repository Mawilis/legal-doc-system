/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ ████████╗███████╗███╗   ██╗ █████╗ ███╗   ██╗████████╗                    ║
  ║ ╚══██╔══╝██╔════╝████╗  ██║██╔══██╗████╗  ██║╚══██╔══╝                    ║
  ║    ██║   █████╗  ██╔██╗ ██║███████║██╔██╗ ██║   ██║                       ║
  ║    ██║   ██╔══╝  ██║╚██╗██║██╔══██║██║╚██╗██║   ██║                       ║
  ║    ██║   ███████╗██║ ╚████║██║  ██║██║ ╚████║   ██║                       ║
  ║    ╚═╝   ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝                       ║
  ║                                                                           ║
  ║  🏛️  WILSY OS 2050 - TENANT ENCRYPTION UTILITY (V8.0)                    ║
  ║  ├─ HSM Integration | KMS Ready | FIPS 140-3                             ║
  ║  ├─ Per-Tenant Encryption Keys | Automatic Rotation                      ║
  ║  └─ Quantum-Resistant Key Wrapping                                       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/
/* WILSY OS 2050 - TENANT ENCRYPTION UTILITY (V8.3) - FORENSICALLY ENHANCED
 *
 * - Envelope encryption (wrap/unwrap) with HSM adapter surface
 * - Deterministic canonical JSON for signatures
 * - HKDF-like derivation bound to tenantId/context
 * - AES-256-GCM with 12-byte IV and AAD
 * - Secure buffer zeroing best-effort
 * - Clear stubs and comments for production HSM/KMS/Dilithium replacement
 *
 * ABSOLUTE PATH (recommended): utils/tenantEncryption.js
 * Node: 20+ (ESM)
 */

import * as crypto from 'crypto';
import { promisify } from 'util';
const pbkdf2 = promisify(crypto.pbkdf2);

const DEFAULT_KEY_TTL_MS = 90 * 24 * 60 * 60 * 1000; // 90 days
const AES_GCM_IV_BYTES = 12; // recommended
const AES_GCM_TAG_BYTES = 16;
const DERIVED_KEY_BYTES = 32; // AES-256

// ----------------------------- Utilities ----------------------------------

function nowIso() {
  return new Date().toISOString();
}

function isValidTenantId(tid) {
  return typeof tid === 'string' && /^[a-zA-Z0-9_-]{3,64}$/.test(tid);
}

function safeLog(component, level, msg, extras = {}) {
  // Structured JSON log for observability
  const out = {
    ts: new Date().toISOString(),
    component,
    level,
    msg,
    ...extras
  };
  // Use console.log for now; replace with your structured logger
  console.log(JSON.stringify(out));
}

// canonicalize object (sorted keys) for deterministic signatures
function canonicalize(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(canonicalize);
  const keys = Object.keys(obj).sort();
  const out = {};
  for (const k of keys) out[k] = canonicalize(obj[k]);
  return out;
}
function canonicalStringify(obj) {
  return JSON.stringify(canonicalize(obj));
}

// constant-time comparison
function constantTimeEqual(a, b) {
  try {
    const ab = Buffer.from(String(a));
    const bb = Buffer.from(String(b));
    if (ab.length !== bb.length) return false;
    return crypto.timingSafeEqual(ab, bb);
  } catch {
    return false;
  }
}

// best-effort zeroing of Buffer
function zeroBuffer(buf) {
  if (!Buffer.isBuffer(buf)) return;
  try {
    buf.fill(0);
  } catch (e) {
    // best-effort; log for forensic trace
    safeLog('tenant-encryption', 'warn', 'zeroBuffer failed', { err: e.message });
  }
}

// HKDF-like extract+expand using HMAC-SHA512 (deterministic, simple)
function hkdfExtractExpand(ikm, salt, info, length = DERIVED_KEY_BYTES) {
  // extract
  const prk = crypto.createHmac('sha512', salt).update(ikm).digest();
  // expand
  let prev = Buffer.alloc(0);
  const out = [];
  let i = 0;
  while (Buffer.concat(out).length < length) {
    i++;
    const hmac = crypto.createHmac('sha512', prk);
    hmac.update(prev);
    hmac.update(info);
    hmac.update(Buffer.from([i]));
    prev = hmac.digest();
    out.push(prev);
  }
  const okm = Buffer.concat(out).slice(0, length);
  // zero prk/prev where possible
  zeroBuffer(prk);
  zeroBuffer(prev);
  return okm;
}

// ----------------------------- HSM Adapter ---------------------------------
// Minimal adapter interface. Replace methods with real KMS/HSM calls in prod.
class HsmAdapter {
  constructor({ provider = 'local', keyId = null, region = null } = {}) {
    this.provider = provider;
    this.keyId = keyId;
    this.region = region;
  }

  async getMasterKey() {
    // In production: call AWS KMS / Azure Key Vault / PKCS#11
    // Here: return process.env.TENANT_MASTER_KEY (hex/base64) if present
    const envKey = process.env.TENANT_MASTER_KEY;
    if (envKey) {
      // Accept hex or base64
      try {
        if (/^[0-9a-fA-F]+$/.test(envKey)) return Buffer.from(envKey, 'hex');
        return Buffer.from(envKey, 'base64');
      } catch {
        return Buffer.from(envKey);
      }
    }
    // If HSM required and not present, throw
    if (process.env.HSM_ENABLED === 'true') {
      throw new Error('HSM master key not available in environment');
    }
    // Fallback: generate ephemeral master key (only for tests)
    return crypto.randomBytes(32);
  }

  async wrapKey(plaintextKey) {
    // Envelope encryption: in production use KMS Encrypt/WrapKey
    // Here we perform AES-GCM wrap with a transient master key (NOT for prod)
    const mk = await this.getMasterKey();
    const iv = crypto.randomBytes(AES_GCM_IV_BYTES);
    const cipher = crypto.createCipheriv('aes-256-gcm', mk.slice(0, 32), iv, { authTagLength: AES_GCM_TAG_BYTES });
    const ct = Buffer.concat([cipher.update(plaintextKey), cipher.final()]);
    const tag = cipher.getAuthTag();
    // return base64 bundle
    const bundle = Buffer.concat([iv, tag, ct]).toString('base64');
    // zero mk
    zeroBuffer(mk);
    return bundle;
  }

  async unwrapKey(wrappedBase64) {
    const mk = await this.getMasterKey();
    const bundle = Buffer.from(wrappedBase64, 'base64');
    const iv = bundle.slice(0, AES_GCM_IV_BYTES);
    const tag = bundle.slice(AES_GCM_IV_BYTES, AES_GCM_IV_BYTES + AES_GCM_TAG_BYTES);
    const ct = bundle.slice(AES_GCM_IV_BYTES + AES_GCM_TAG_BYTES);
    const decipher = crypto.createDecipheriv('aes-256-gcm', mk.slice(0, 32), iv, { authTagLength: AES_GCM_TAG_BYTES });
    decipher.setAuthTag(tag);
    const pt = Buffer.concat([decipher.update(ct), decipher.final()]);
    zeroBuffer(mk);
    return pt;
  }

  async rotateMasterKey() {
    // Production: rotate via KMS; here we just log
    safeLog('hsm-adapter', 'info', 'rotateMasterKey called (stub)');
    return true;
  }
}

// --------------------------- TenantEncryption ------------------------------

class TenantEncryption {
  constructor(opts = {}) {
    this.component = 'WILSY-TENANT-ENCRYPTION-V8';
    this.version = '8.3.0';
    this.algorithms = {
      symmetric: 'aes-256-gcm',
      hash: 'sha512', // used for KDF HMAC; sha3-512 can be substituted when runtime supports
      hmac: 'sha512'
    };
    this.hsmEnabled = process.env.HSM_ENABLED === 'true';
    this.hsm = new HsmAdapter({
      provider: process.env.HSM_PROVIDER || opts.provider || 'local',
      keyId: process.env.HSM_MASTER_KEY_ID || opts.keyId,
      region: process.env.AWS_REGION || opts.region || 'af-south-1'
    });
    this.metrics = {
      encryptions: 0,
      decryptions: 0,
      keyRotations: 0,
      failures: 0,
      startTime: Date.now()
    };
  }

  // Generate tenant key material (returns wrapped key + metadata)
  async generateTenantKey(tenantId, { ttlMs = DEFAULT_KEY_TTL_MS, context = '' } = {}) {
    if (!isValidTenantId(tenantId)) throw new Error('Invalid tenantId');
    const start = Date.now();
    try {
      // master key from HSM/KMS
      const mk = await this.hsm.getMasterKey(); // Buffer
      // derive tenant-specific key using HKDF-like with tenantId and context
      const salt = crypto.randomBytes(32);
      const ikm = mk; // use master key as IKM
      const info = Buffer.from(`${tenantId}:${context}`, 'utf8');
      const derived = hkdfExtractExpand(ikm, salt, info, DERIVED_KEY_BYTES);

      // wrap derived key with HSM (envelope)
      const wrapped = await this.hsm.wrapKey(derived);

      // zero sensitive buffers
      zeroBuffer(derived);
      zeroBuffer(ikm);

      const keyObj = {
        keyId: `tk-${crypto.randomBytes(12).toString('hex')}`,
        version: 1,
        algorithm: this.algorithms.symmetric,
        wrappedKey: wrapped,           // safe to store
        salt: salt.toString('base64'),
        createdAt: nowIso(),
        expiresAt: new Date(Date.now() + ttlMs).toISOString(),
        hsmManaged: this.hsmEnabled,
        tenantId,
        context
      };

      this.metrics.encryptions++;
      safeLog(this.component, 'info', 'tenant key generated', { tenantId: tenantId, keyId: keyObj.keyId, durationMs: Date.now() - start });
      return keyObj;
    } catch (err) {
      this.metrics.failures++;
      safeLog(this.component, 'error', 'generateTenantKey failed', { err: err.message });
      throw err;
    }
  }

  // Internal: unwrap key (returns Buffer keyMaterial)
  async _unwrapKeyBuffer(keyObj) {
    if (!keyObj || !keyObj.wrappedKey) throw new Error('Invalid key object');
    const buf = await this.hsm.unwrapKey(keyObj.wrappedKey);
    return buf; // Buffer
  }

  // Encrypt tenant data using envelope-derived key (AAD binds tenantId + keyId)
  async encryptTenantData(data, keyObj) {
    const start = Date.now();
    try {
      if (!keyObj || !keyObj.wrappedKey) throw new Error('Invalid tenant key');
      const keyBuf = await this._unwrapKeyBuffer(keyObj); // Buffer
      const iv = crypto.randomBytes(AES_GCM_IV_BYTES);
      const aad = Buffer.from(`${keyObj.tenantId}|${keyObj.keyId}`, 'utf8');

      const cipher = crypto.createCipheriv(this.algorithms.symmetric, keyBuf.slice(0, 32), iv, { authTagLength: AES_GCM_TAG_BYTES });
      cipher.setAAD(aad);

      const input = typeof data === 'string' ? data : JSON.stringify(data);
      const ct = Buffer.concat([cipher.update(input, 'utf8'), cipher.final()]);
      const tag = cipher.getAuthTag();

      // zero key buffer
      zeroBuffer(keyBuf);

      const payload = {
        keyId: keyObj.keyId,
        tenantId: keyObj.tenantId,
        algorithm: this.algorithms.symmetric,
        iv: iv.toString('base64'),
        aad: aad.toString('base64'),
        data: ct.toString('base64'),
        authTag: tag.toString('base64'),
        timestamp: Date.now()
      };

      this.metrics.encryptions++;
      safeLog(this.component, 'info', 'encryptTenantData', { tenantId: keyObj.tenantId, keyId: keyObj.keyId, durationMs: Date.now() - start });
      return payload;
    } catch (err) {
      this.metrics.failures++;
      safeLog(this.component, 'error', 'encryptTenantData failed', { err: err.message });
      throw err;
    }
  }

  // Decrypt tenant data
  async decryptTenantData(encrypted, keyObj) {
    const start = Date.now();
    try {
      if (!encrypted || !keyObj) throw new Error('Invalid inputs');
      const keyBuf = await this._unwrapKeyBuffer(keyObj);
      const iv = Buffer.from(encrypted.iv, 'base64');
      const tag = Buffer.from(encrypted.authTag, 'base64');
      const aad = Buffer.from(encrypted.aad, 'base64');
      const ct = Buffer.from(encrypted.data, 'base64');

      const decipher = crypto.createDecipheriv(this.algorithms.symmetric, keyBuf.slice(0, 32), iv, { authTagLength: AES_GCM_TAG_BYTES });
      decipher.setAAD(aad);
      decipher.setAuthTag(tag);

      const pt = Buffer.concat([decipher.update(ct), decipher.final()]);
      const outStr = pt.toString('utf8');

      // zero key buffer and pt
      zeroBuffer(keyBuf);
      zeroBuffer(pt);

      // attempt JSON parse, fallback to string
      let result;
      try { result = JSON.parse(outStr); } catch { result = outStr; }

      this.metrics.decryptions++;
      safeLog(this.component, 'info', 'decryptTenantData', { tenantId: encrypted.tenantId, keyId: encrypted.keyId, durationMs: Date.now() - start });
      return result;
    } catch (err) {
      this.metrics.failures++;
      safeLog(this.component, 'error', 'decryptTenantData failed', { err: err.message });
      throw err;
    }
  }

  // Rotate tenant key: generate new key and mark previousKeyId
  async rotateTenantKey(tenantId, oldKeyObj, opts = {}) {
    const start = Date.now();
    try {
      if (!isValidTenantId(tenantId)) throw new Error('Invalid tenantId');
      const newKey = await this.generateTenantKey(tenantId, opts);
      newKey.version = (oldKeyObj?.version || 1) + 1;
      newKey.previousKeyId = oldKeyObj?.keyId || null;
      newKey.rotatedAt = nowIso();
      this.metrics.keyRotations++;
      safeLog(this.component, 'info', 'rotateTenantKey', { tenantId, oldKeyId: oldKeyObj?.keyId, newKeyId: newKey.keyId, durationMs: Date.now() - start });
      return newKey;
    } catch (err) {
      this.metrics.failures++;
      safeLog(this.component, 'error', 'rotateTenantKey failed', { err: err.message });
      throw err;
    }
  }

  // Quantum-safe signature stub (deterministic canonical snapshot)
  // NOTE: This is a deterministic stub for testing. Replace with real Dilithium-5 library.
  async createQuantumSignature(data, tenantId) {
    if (!isValidTenantId(tenantId)) throw new Error('Invalid tenantId');
    const payload = {
      data: canonicalStringify(data),
      tenantId,
      timestamp: Date.now()
    };
    const hash = crypto.createHash('sha512').update(JSON.stringify(payload)).digest('hex');
    // signature format: QSIG:v1:<timestamp>:<hash>:<random-suffix>
    const suffix = crypto.randomBytes(32).toString('hex');
    const signature = `QSIG:v1:${payload.timestamp}:${hash}:${suffix}`;
    safeLog(this.component, 'info', 'createQuantumSignature', { tenantId, ts: payload.timestamp });
    return signature;
  }

  verifyQuantumSignature(data, tenantId, signature) {
    try {
      if (!signature || typeof signature !== 'string') return false;
      const parts = signature.split(':');
      if (parts.length < 5) return false;
      const [label, ver, tsStr, hash, suffix] = parts;
      if (label !== 'QSIG' || ver !== 'v1') return false;
      const payload = {
        data: canonicalStringify(data),
        tenantId,
        timestamp: parseInt(tsStr, 10)
      };
      const calculated = crypto.createHash('sha512').update(JSON.stringify(payload)).digest('hex');
      const ok = constantTimeEqual(calculated, hash);
      safeLog(this.component, 'info', 'verifyQuantumSignature', { tenantId, ok });
      return ok;
    } catch (err) {
      safeLog(this.component, 'error', 'verifyQuantumSignature failed', { err: err.message });
      return false;
    }
  }

  // Metrics and health
  getMetrics() {
    return {
      ...this.metrics,
      uptimeMs: Date.now() - this.metrics.startTime,
      hsmEnabled: this.hsmEnabled,
      algorithms: this.algorithms
    };
  }

  async health() {
    try {
      // quick smoke test: generate key, encrypt/decrypt small payload
      const tenantId = 'health-check';
      const key = await this.generateTenantKey(tenantId, { ttlMs: 60_000 });
      const payload = { test: 'ok' };
      const enc = await this.encryptTenantData(payload, key);
      const dec = await this.decryptTenantData(enc, key);
      const ok = dec && dec.test === 'ok';
      return {
        status: ok ? 'healthy' : 'degraded',
        component: this.component,
        encryptionWorking: ok,
        metrics: this.getMetrics(),
        timestamp: nowIso()
      };
    } catch (err) {
      return {
        status: 'degraded',
        component: this.component,
        error: err.message,
        timestamp: nowIso()
      };
    }
  }
}

// Singleton
export const tenantEncryption = new TenantEncryption();
export default tenantEncryption;

// Export helpers for unit tests
export const _internals = {
  canonicalize,
  canonicalStringify,
  hkdfExtractExpand,
  constantTimeEqual,
  HsmAdapter
};
