/**
 * TITLE: WILSY OS Python Authority Transport
 * VERSION: v1.0.0-WILSY-NODE-PYTHON-INTEROP
 * AUTHORITY: Foreign-runtime transport/signing adapter only. Python EOS owns verification.
 * EPITOME: Signs deterministic protocol-v1 service assertions over exact outbound bytes.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/pythonAuthorityTransport.js
 * COLLABORATION / OWNERSHIP: Node transport consumed by Python EOS authority.
 * CERTIFICATION/UPDATE DATE: 2026-08-30
 * SECURITY / PRIVACY POSTURE: No user authority, tenant truth, or secrets in assertions.
 * TENANT BOUNDARY: Does not own tenant membership.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
 * FAIL-CLOSED POSTURE: Missing or malformed configuration throws.
 */
import crypto from 'node:crypto';

export const PROTOCOL_VERSION = 'v1';
export const resolveInternalAuthConfig = (env = process.env) => {
  const fields = [
    ['service_id', 'WILSY_INTERNAL_AUTH_SERVICE_ID'],
    ['audience', 'WILSY_INTERNAL_AUTH_AUDIENCE'],
    ['key_id', 'WILSY_INTERNAL_AUTH_KEY_ID'],
    ['secret', 'WILSY_INTERNAL_AUTH_SECRET'],
  ];
  const config = {};
  for (const [name, key] of fields) {
    if (typeof env[key] !== 'string' || env[key].length === 0)
      throw new Error(`INTERNAL_AUTH_${name.toUpperCase()}_MISSING`);
    config[name] = env[key];
  }
  return config;
};
export const sha3Body = (body) => crypto.createHash('sha3-512').update(body).digest('hex');
export const canonicalizeServiceAssertion = ({
  version,
  service_id,
  audience,
  method,
  path,
  timestamp,
  nonce,
  body_sha3_512,
  correlation_id,
}) =>
  [
    version,
    service_id,
    audience,
    method,
    path,
    timestamp,
    nonce,
    body_sha3_512,
    correlation_id,
  ].join('\n');
export const signServiceAssertion = ({
  body,
  timestamp,
  nonce,
  service_id,
  audience,
  key_id,
  secret,
  method,
  path,
  correlation_id,
}) => {
  const exactBody = Buffer.isBuffer(body)
    ? body
    : Buffer.from(body instanceof Uint8Array ? body : JSON.stringify(body), 'utf8');
  const fields = {
    version: PROTOCOL_VERSION,
    service_id,
    audience,
    method,
    path,
    timestamp: String(timestamp),
    nonce,
    body_sha3_512: sha3Body(exactBody),
    correlation_id,
  };
  const canonical = canonicalizeServiceAssertion(fields);
  const signature = crypto
    .createHmac('sha256', secret)
    .update(Buffer.from(canonical, 'utf8'))
    .digest('hex');
  return {
    headers: {
      'X-Wilsy-Auth-Version': fields.version,
      'X-Wilsy-Service-ID': service_id,
      'X-Wilsy-Audience': audience,
      'X-Wilsy-Key-ID': key_id,
      'X-Wilsy-Timestamp': fields.timestamp,
      'X-Wilsy-Nonce': nonce,
      'X-Wilsy-Body-SHA3-512': fields.body_sha3_512,
      'X-Wilsy-Correlation-ID': correlation_id,
      'X-Wilsy-Signature': signature,
    },
    body: exactBody,
    canonical,
    signature,
  };
};

// ARTIFACT: pythonAuthorityTransport.js
// VERSION: v1.0.0-WILSY-NODE-PYTHON-INTEROP
// AUTHORITY BOUNDARY: Foreign-runtime transport/signing adapter only.
// TENANT POSTURE: No tenant authority.
// FAIL-CLOSED POSTURE: Missing or malformed configuration throws.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
// END OF WILSY OS SOVEREIGN ARTIFACT
