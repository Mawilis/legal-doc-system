import CryptoJS from 'crypto-js';


const subtle = globalThis.crypto?.subtle;

if (!subtle) {
  throw new Error('WEB_CRYPTO_SUBTLE_UNAVAILABLE');
}

const encoder = new TextEncoder();
const decoder = new TextDecoder();

function normalizeInput(data) {
  return typeof data === 'object'
    ? JSON.stringify(data)
    : String(data);
}

function bytesToHex(bytes) {
  return Array.from(
    bytes,
    byte => byte.toString(16).padStart(2, '0'),
  ).join('');
}

function hexToBytes(hex) {
  if (
    typeof hex !== 'string' ||
    hex.length % 2 !== 0 ||
    !/^[0-9a-f]*$/i.test(hex)
  ) {
    throw new Error('INVALID_HEX');
  }

  const out = new Uint8Array(hex.length / 2);

  for (let i = 0; i < out.length; i += 1) {
    out[i] = Number.parseInt(
      hex.slice(i * 2, i * 2 + 2),
      16,
    );
  }

  return out;
}

function concatBytes(...arrays) {
  const size = arrays.reduce(
    (sum, item) => sum + item.length,
    0,
  );

  const out = new Uint8Array(size);
  let offset = 0;

  for (const item of arrays) {
    out.set(item, offset);
    offset += item.length;
  }

  return out;
}

function bytesToBase64(bytes) {
  let binary = '';

  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }

  return btoa(binary);
}

function base64ToBytes(value) {
  const binary = atob(value);
  const out = new Uint8Array(binary.length);

  for (let i = 0; i < binary.length; i += 1) {
    out[i] = binary.charCodeAt(i);
  }

  return out;
}

function derToPem(der, label) {
  const base64 = bytesToBase64(
    new Uint8Array(der),
  );

  const body = base64.match(/.{1,64}/g)?.join('\n') ?? '';

  return (
    `-----BEGIN ${label}-----\n` +
    `${body}\n` +
    `-----END ${label}-----\n`
  );
}

function pemToDer(pem, label) {
  const start = `-----BEGIN ${label}-----`;
  const end = `-----END ${label}-----`;

  if (
    !pem.includes(start) ||
    !pem.includes(end)
  ) {
    throw new Error(
      `INVALID_${label.replaceAll(' ', '_')}_PEM`,
    );
  }

  const base64 = pem
    .replace(start, '')
    .replace(end, '')
    .replace(/\s+/g, '');

  return base64ToBytes(base64);
}

function encodeDerLength(length) {
  if (length < 0x80) {
    return new Uint8Array([length]);
  }

  const bytes = [];
  let value = length;

  while (value > 0) {
    bytes.unshift(value & 0xff);
    value >>>= 8;
  }

  return new Uint8Array([
    0x80 | bytes.length,
    ...bytes,
  ]);
}

function readDerLength(bytes, offset) {
  const first = bytes[offset];

  if (first < 0x80) {
    return {
      length: first,
      next: offset + 1,
    };
  }

  const count = first & 0x7f;

  if (
    count === 0 ||
    count > 4 ||
    offset + count >= bytes.length
  ) {
    throw new Error('INVALID_DER_LENGTH');
  }

  let length = 0;

  for (let i = 0; i < count; i += 1) {
    length = (
      length * 256 +
      bytes[offset + 1 + i]
    );
  }

  return {
    length,
    next: offset + 1 + count,
  };
}

function trimInteger(bytes) {
  let start = 0;

  while (
    start < bytes.length - 1 &&
    bytes[start] === 0
  ) {
    start += 1;
  }

  let value = bytes.slice(start);

  if (value[0] & 0x80) {
    value = concatBytes(
      new Uint8Array([0]),
      value,
    );
  }

  return value;
}

function rawP384SignatureToDer(raw) {
  const bytes = new Uint8Array(raw);

  if (bytes.length !== 96) {
    throw new Error(
      `INVALID_P384_RAW_SIGNATURE_LENGTH:${bytes.length}`,
    );
  }

  const r = trimInteger(
    bytes.slice(0, 48),
  );
  const s = trimInteger(
    bytes.slice(48),
  );

  const rPart = concatBytes(
    new Uint8Array([0x02]),
    encodeDerLength(r.length),
    r,
  );

  const sPart = concatBytes(
    new Uint8Array([0x02]),
    encodeDerLength(s.length),
    s,
  );

  const body = concatBytes(
    rPart,
    sPart,
  );

  return concatBytes(
    new Uint8Array([0x30]),
    encodeDerLength(body.length),
    body,
  );
}

function derP384SignatureToRaw(der) {
  const bytes = (
    der instanceof Uint8Array
      ? der
      : new Uint8Array(der)
  );

  let offset = 0;

  if (bytes[offset++] !== 0x30) {
    throw new Error('DER_SIGNATURE_NOT_SEQUENCE');
  }

  const seq = readDerLength(
    bytes,
    offset,
  );

  offset = seq.next;

  const sequenceEnd = offset + seq.length;

  function readInteger() {
    if (bytes[offset++] !== 0x02) {
      throw new Error('DER_SIGNATURE_INTEGER_EXPECTED');
    }

    const info = readDerLength(
      bytes,
      offset,
    );

    offset = info.next;

    let value = bytes.slice(
      offset,
      offset + info.length,
    );

    offset += info.length;

    while (
      value.length > 48 &&
      value[0] === 0
    ) {
      value = value.slice(1);
    }

    if (value.length > 48) {
      throw new Error(
        'DER_SIGNATURE_INTEGER_TOO_LARGE',
      );
    }

    const padded = new Uint8Array(48);

    padded.set(
      value,
      48 - value.length,
    );

    return padded;
  }

  const r = readInteger();
  const s = readInteger();

  if (offset !== sequenceEnd) {
    throw new Error(
      'DER_SIGNATURE_TRAILING_BYTES',
    );
  }

  return concatBytes(r, s);
}

export function generateHash(
  data,
  prefixed = true,
) {
  const input = normalizeInput(data);
  const hex = CryptoJS
    .SHA256(input)
    .toString(CryptoJS.enc.Hex);

  return prefixed
    ? `hash:${hex}`
    : hex;
}

export function generateHmac(
  data,
  key,
) {
  const input = normalizeInput(data);

  return (
    'hmac:' +
    CryptoJS
      .HmacSHA384(
        input,
        String(key),
      )
      .toString(CryptoJS.enc.Hex)
  );
}

export function randomBytes(
  length = 32,
) {
  const bytes = new Uint8Array(length);

  globalThis.crypto.getRandomValues(
    bytes,
  );

  return bytesToHex(bytes);
}

export function generateUUID() {
  return globalThis.crypto.randomUUID();
}

export function secureCompare(a, b) {
  if (
    typeof a !== 'string' ||
    typeof b !== 'string'
  ) {
    return false;
  }

  const left = encoder.encode(
    a.padEnd(64, '\0'),
  );

  const right = encoder.encode(
    b.padEnd(64, '\0'),
  );

  if (left.length !== right.length) {
    return false;
  }

  let diff = 0;

  for (let i = 0; i < left.length; i += 1) {
    diff |= (
      left[i] ^
      right[i]
    );
  }

  return diff === 0;
}

export async function encrypt(
  data,
  key,
) {
  const rawKey = hexToBytes(key);

  if (rawKey.length !== 32) {
    throw new Error(
      'AES_256_GCM_KEY_MUST_BE_32_BYTES',
    );
  }

  const iv = new Uint8Array(16);

  globalThis.crypto.getRandomValues(iv);

  const cryptoKey = await subtle.importKey(
    'raw',
    rawKey,
    {
      name: 'AES-GCM',
    },
    false,
    ['encrypt'],
  );

  const sealed = new Uint8Array(
    await subtle.encrypt(
      {
        name: 'AES-GCM',
        iv,
        tagLength: 128,
      },
      cryptoKey,
      encoder.encode(
        JSON.stringify(data),
      ),
    ),
  );

  const encrypted = sealed.slice(
    0,
    sealed.length - 16,
  );

  const authTag = sealed.slice(
    sealed.length - 16,
  );

  return {
    encrypted: bytesToHex(encrypted),
    iv: bytesToHex(iv),
    authTag: bytesToHex(authTag),
  };
}

export async function decrypt(
  encryptedData,
  key,
) {
  const rawKey = hexToBytes(key);

  if (rawKey.length !== 32) {
    throw new Error(
      'AES_256_GCM_KEY_MUST_BE_32_BYTES',
    );
  }

  const cryptoKey = await subtle.importKey(
    'raw',
    rawKey,
    {
      name: 'AES-GCM',
    },
    false,
    ['decrypt'],
  );

  const sealed = concatBytes(
    hexToBytes(
      encryptedData.encrypted,
    ),
    hexToBytes(
      encryptedData.authTag,
    ),
  );

  const plain = await subtle.decrypt(
    {
      name: 'AES-GCM',
      iv: hexToBytes(
        encryptedData.iv,
      ),
      tagLength: 128,
    },
    cryptoKey,
    sealed,
  );

  return JSON.parse(
    decoder.decode(plain),
  );
}

export async function generateKeyPair() {
  const pair = await subtle.generateKey(
    {
      name: 'ECDSA',
      namedCurve: 'P-384',
    },
    true,
    ['sign', 'verify'],
  );

  const publicDer = await subtle.exportKey(
    'spki',
    pair.publicKey,
  );

  const privateDer = await subtle.exportKey(
    'pkcs8',
    pair.privateKey,
  );

  return {
    publicKey: derToPem(
      publicDer,
      'PUBLIC KEY',
    ),
    privateKey: derToPem(
      privateDer,
      'PRIVATE KEY',
    ),
  };
}

export async function sign(
  data,
  privateKey,
) {
  const key = await subtle.importKey(
    'pkcs8',
    pemToDer(
      privateKey,
      'PRIVATE KEY',
    ),
    {
      name: 'ECDSA',
      namedCurve: 'P-384',
    },
    false,
    ['sign'],
  );

  const raw = await subtle.sign(
    {
      name: 'ECDSA',
      hash: 'SHA-384',
    },
    key,
    encoder.encode(
      JSON.stringify(data),
    ),
  );

  return bytesToHex(
    rawP384SignatureToDer(raw),
  );
}

export async function verify(
  data,
  signature,
  publicKey,
) {
  const key = await subtle.importKey(
    'spki',
    pemToDer(
      publicKey,
      'PUBLIC KEY',
    ),
    {
      name: 'ECDSA',
      namedCurve: 'P-384',
    },
    false,
    ['verify'],
  );

  const raw = derP384SignatureToRaw(
    hexToBytes(signature),
  );

  return subtle.verify(
    {
      name: 'ECDSA',
      hash: 'SHA-384',
    },
    key,
    raw,
    encoder.encode(
      JSON.stringify(data),
    ),
  );
}

export function createMerkleProof(
  hashes,
  targetHash,
) {
  const proof = [];
  let index = hashes.indexOf(
    targetHash,
  );

  if (index === -1) {
    return null;
  }

  let level = [...hashes];
  let levelIndex = index;

  while (level.length > 1) {
    const nextLevel = [];
    const isLeft = (
      levelIndex % 2 === 0
    );

    const siblingIndex = (
      isLeft
        ? levelIndex + 1
        : levelIndex - 1
    );

    if (siblingIndex < level.length) {
      proof.push({
        position: (
          isLeft
            ? 'right'
            : 'left'
        ),
        hash: level[siblingIndex],
      });
    }

    for (
      let i = 0;
      i < level.length;
      i += 2
    ) {
      if (i + 1 < level.length) {
        const combined = (
          level[i] +
          level[i + 1]
        );

        nextLevel.push(
          generateHash(
            combined,
            false,
          ),
        );
      } else {
        nextLevel.push(
          level[i],
        );
      }
    }

    level = nextLevel;
    levelIndex = Math.floor(
      levelIndex / 2,
    );
  }

  return {
    targetHash,
    proof,
    root: level[0],
  };
}

export function verifyMerkleProof(
  targetHash,
  proof,
  root,
) {
  let hash = targetHash;

  for (const step of proof) {
    hash = (
      step.position === 'left'
        ? generateHash(
            step.hash + hash,
            false,
          )
        : generateHash(
            hash + step.hash,
            false,
          )
    );
  }

  return hash === root;
}

export const hash = data => (
  typeof data === 'string'
    ? data
    : JSON.stringify(data)
);
