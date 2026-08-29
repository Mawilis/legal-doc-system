/**
 * WILSY OS FOREIGN-RUNTIME AUTHENTICATION OUTAGE OBSERVATION ADAPTER
 *
 * TITLE: WILSY OS Authentication Outage Node Observation Adapter
 * VERSION: v1.0.0-PYTHON-CROSS-CERT-ADAPTER
 * AUTHORITY: Foreign-runtime observation capability only. This artifact owns no
 *            Wilsy OS certification verdict, business truth, tenant authority,
 *            role authority, or financial execution authority.
 * EPITOME: Persistent JSONL Node/Mongoose/User/middleware adapter that executes
 *          one Python-commanded operation at a time and returns bounded raw facts.
 * ABSOLUTE CANONICAL PATH:
 *   /Users/wilsonkhanyezi/legal-doc-system/server/tests/security/helpers/authPersistenceOutage.child.mjs
 * COLLABORATION / OWNERSHIP:
 *   Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
 *   AI Collaborator: Core Systems Engineering Agent
 * CERTIFICATION/UPDATE DATE: 2026-08-29
 * CHANGELOG:
 *   v1.0.0-PYTHON-CROSS-CERT-ADAPTER replaces legacy IPC-driven outage verdict
 *   logic with the closed Python-owned JSONL protocol and raw observations only.
 * COMPLIANCE:
 *   WILSY OS Sovereign Codex Governance Contract
 *   v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
 * SECURITY / PRIVACY POSTURE:
 *   Fail closed. Synthetic fixture values only. A process-local ephemeral JWT
 *   signing key exists only inside this child process and is never serialized.
 *   Raw credentials, tokens, authorization headers, passwords, password hashes,
 *   complete user documents, and designated-email identifiers are prohibited
 *   from protocol output.
 * TENANT BOUNDARY:
 *   Synthetic tenant-shaped fixture data exists only to satisfy the real User
 *   model. It establishes no governed tenant membership or authorization truth.
 * AUTHORITY BOUNDARY:
 *   Python owns process lifecycle, Mongo lifecycle, sequencing, causal
 *   classification, evidence, SHA3-512, final status, and restoration. Node owns
 *   only real foreign-runtime execution and bounded raw observations.
 * FINANCIAL AUTHORITY BOUNDARY:
 *   None. Kennel EOS remains the exclusive financial execution authority.
 */

import crypto from 'node:crypto';
import process from 'node:process';
import readline from 'node:readline';
import util from 'node:util';

const VERSION = 'v1.0.0-PYTHON-CROSS-CERT-ADAPTER';
const PROTOCOL_VERSION = String(process.env.WILSY_AUTH_CERT_PROTOCOL_VERSION || '').trim();
const MONGO_HOST = String(process.env.WILSY_AUTH_CERT_MONGO_HOST || '').trim();
const MONGO_PORT = String(process.env.WILSY_AUTH_CERT_MONGO_PORT || '').trim();
const MONGO_REPLICA_SET = String(process.env.WILSY_AUTH_CERT_REPLICA_SET || '').trim();
const DATABASE_NAME = String(process.env.WILSY_AUTH_CERT_DATABASE || '').trim();
const SELECTION_TIMEOUT_MS = Number(process.env.WILSY_AUTH_CERT_NODE_SELECTION_TIMEOUT_MS);
const HEARTBEAT_FREQUENCY_MS = Number(process.env.WILSY_AUTH_CERT_NODE_HEARTBEAT_FREQUENCY_MS);

const COMMANDS = Object.freeze([
  'INITIALIZE_RUNTIME',
  'PROVISION_FIXTURE',
  'LOOKUP_FIXTURE',
  'DELETE_FIXTURE',
  'RUN_SCENARIO',
  'CLOSE_RUNTIME',
]);

const SCENARIOS = Object.freeze([
  'PRIMARY_USER_FOUND',
  'PRIMARY_SOVEREIGN_USER_FOUND',
  'SECONDARY_USER_FOUND',
  'PRIMARY_DB_FAILURE',
  'PRIMARY_PRIVILEGED_ROLE_DB_FAILURE',
  'PRIMARY_SECURITY_CLEARANCE_DB_FAILURE',
  'PRIMARY_TENANT_DB_FAILURE',
  'PRIMARY_SOVEREIGN_DB_FAILURE',
  'SECONDARY_DB_FAILURE',
  'SECONDARY_PRIVILEGED_ROLE_DB_FAILURE',
  'DESIGNATED_EMAIL_DB_FAILURE',
  'SECONDARY_SECURITY_CLEARANCE_DB_FAILURE',
  'SECONDARY_TENANT_DB_FAILURE',
]);

const OUTAGE_SCENARIOS = new Set(SCENARIOS.slice(3));

const FORBIDDEN_OUTPUT_KEYS = new Set([
  'authorization',
  'designated_email',
  'full_user',
  'jwt',
  'jwt_secret',
  'password',
  'password_hash',
  'passwordhash',
  'raw_user',
  'token',
]);

const MAX_DIAGNOSTIC_LENGTH = 240;
const MAX_RESPONSE_CODE_LENGTH = 120;

let mongoose = null;
let User = null;
let primary = null;
let secondary = null;
let jwt = null;
let initialized = false;
let closing = false;

const fixtureRegistry = new Map();

/*
 * stdout is protocol-exclusive. Redirect all ordinary console surfaces to
 * stderr before importing repository modules because model/middleware code may
 * log during initialization, persistence, or outage handling.
 */
const writeDiagnostic = (...args) => {
  const rendered = util.format(...args);
  process.stderr.write(`${rendered}\n`);
};
console.log = writeDiagnostic;
console.info = writeDiagnostic;
console.warn = writeDiagnostic;
console.error = writeDiagnostic;

const failConfiguration = (message) => {
  const error = new Error(message);
  error.name = 'AdapterConfigurationError';
  throw error;
};

const requireConfiguration = () => {
  for (const [name, value] of [
    ['WILSY_AUTH_CERT_PROTOCOL_VERSION', PROTOCOL_VERSION],
    ['WILSY_AUTH_CERT_MONGO_HOST', MONGO_HOST],
    ['WILSY_AUTH_CERT_MONGO_PORT', MONGO_PORT],
    ['WILSY_AUTH_CERT_REPLICA_SET', MONGO_REPLICA_SET],
    ['WILSY_AUTH_CERT_DATABASE', DATABASE_NAME],
  ]) {
    if (!value) failConfiguration(`${name} is unavailable`);
  }

  if (!Number.isInteger(SELECTION_TIMEOUT_MS) || SELECTION_TIMEOUT_MS <= 0) {
    failConfiguration('Node selection timeout is invalid');
  }
  if (!Number.isInteger(HEARTBEAT_FREQUENCY_MS) || HEARTBEAT_FREQUENCY_MS <= 0) {
    failConfiguration('Node heartbeat frequency is invalid');
  }
};

requireConfiguration();

/*
 * Synthetic, process-local cryptographic material only. It deliberately
 * overrides inherited credential configuration inside this child process so
 * certification never consumes or reveals a production JWT secret.
 */
const EPHEMERAL_JWT_SECRET = crypto.randomBytes(64).toString('hex');
process.env.JWT_SECRET = EPHEMERAL_JWT_SECRET;
delete process.env.JWT_SECRETS;

const mongoUri = () => {
  const encodedDb = encodeURIComponent(DATABASE_NAME);
  const encodedReplicaSet = encodeURIComponent(MONGO_REPLICA_SET);
  return (
    `mongodb://${MONGO_HOST}:${MONGO_PORT}/${encodedDb}` +
    `?replicaSet=${encodedReplicaSet}` +
    `&serverSelectionTimeoutMS=${SELECTION_TIMEOUT_MS}`
  );
};

const isPlainObject = (value) =>
  value !== null &&
  typeof value === 'object' &&
  !Array.isArray(value) &&
  Object.getPrototypeOf(value) === Object.prototype;

const requireExactKeys = (value, expected, context) => {
  if (!isPlainObject(value)) {
    throw new TypeError(`${context} must be a JSON object`);
  }
  const actual = Object.keys(value).sort();
  const required = [...expected].sort();
  if (actual.length !== required.length || actual.some((key, index) => key !== required[index])) {
    throw new TypeError(`${context} field contract mismatch`);
  }
};

const requireTrimmedString = (value, context) => {
  if (typeof value !== 'string' || value.length === 0 || value !== value.trim()) {
    throw new TypeError(`${context} must be a non-empty trimmed string`);
  }
  return value;
};

const requireNullableTrimmedString = (value, context) => {
  if (value === null) return null;
  return requireTrimmedString(value, context);
};

const requireBoolean = (value, context) => {
  if (typeof value !== 'boolean') {
    throw new TypeError(`${context} must be boolean`);
  }
  return value;
};

const requireJsonValue = (value, path = '$', depth = 0) => {
  if (depth > 32) {
    throw new TypeError(`${path} exceeds protocol depth`);
  }
  if (value === null || typeof value === 'string' || typeof value === 'boolean') {
    return;
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) {
      throw new TypeError(`${path} contains non-finite number`);
    }
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => requireJsonValue(item, `${path}[${index}]`, depth + 1));
    return;
  }
  if (isPlainObject(value)) {
    for (const [key, item] of Object.entries(value)) {
      if (FORBIDDEN_OUTPUT_KEYS.has(key.toLowerCase())) {
        throw new TypeError(`${path} contains forbidden protocol key`);
      }
      requireJsonValue(item, `${path}.${key}`, depth + 1);
    }
    return;
  }
  throw new TypeError(`${path} contains unsupported protocol value`);
};

const sanitizeDiagnostic = (value) => {
  if (typeof value !== 'string') return null;
  let sanitized = value
    .replace(/Bearer\s+[A-Za-z0-9._~+/=-]+/gi, 'Bearer [REDACTED]')
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, '[REDACTED_EMAIL]')
    .replace(/[A-F0-9]{64,}/gi, '[REDACTED_HEX]')
    .replace(/\s+/g, ' ')
    .trim();

  if (!sanitized) return null;
  if (sanitized.length > MAX_DIAGNOSTIC_LENGTH) {
    sanitized = sanitized.slice(0, MAX_DIAGNOSTIC_LENGTH);
  }
  return sanitized;
};

const boundedStringOrNull = (value, limit) => {
  if (typeof value !== 'string') return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  return trimmed.slice(0, limit);
};

const writeEnvelope = async (operationId, type, payload) => {
  requireTrimmedString(operationId, 'response operation_id');
  requireTrimmedString(type, 'response type');
  requireJsonValue(payload, '$.payload');

  const envelope = {
    protocol_version: PROTOCOL_VERSION,
    operation_id: operationId,
    type,
    payload,
  };
  requireJsonValue(envelope);

  const encoded = JSON.stringify(envelope);
  if (process.stdout.write(`${encoded}\n`)) return;

  await new Promise((resolve, reject) => {
    const onDrain = () => {
      cleanup();
      resolve();
    };
    const onError = (error) => {
      cleanup();
      reject(error);
    };
    const cleanup = () => {
      process.stdout.off('drain', onDrain);
      process.stdout.off('error', onError);
    };
    process.stdout.once('drain', onDrain);
    process.stdout.once('error', onError);
  });
};

const writeError = async (operationId, error) => {
  const errorType = boundedStringOrNull(error?.name, 120) || 'AdapterRuntimeError';
  const message = sanitizeDiagnostic(error?.message) || 'foreign-runtime adapter operation failed';

  await writeEnvelope(operationId, 'ERROR', {
    error_type: errorType,
    message,
  });
};

const parseRequestLine = (line) => {
  let parsed;
  try {
    parsed = JSON.parse(line);
  } catch (parseError) {
    const error = new SyntaxError('request contains malformed JSON');
    error.name = 'AdapterProtocolError';
    error.cause = parseError;
    throw error;
  }

  requireExactKeys(
    parsed,
    ['protocol_version', 'operation_id', 'command', 'payload'],
    'request envelope'
  );

  const protocolVersion = requireTrimmedString(parsed.protocol_version, 'request protocol_version');
  const operationId = requireTrimmedString(parsed.operation_id, 'request operation_id');
  const command = requireTrimmedString(parsed.command, 'request command');

  if (protocolVersion !== PROTOCOL_VERSION) {
    throw Object.assign(new Error('request protocol version mismatch'), {
      name: 'AdapterProtocolError',
      operationId,
    });
  }
  if (!COMMANDS.includes(command)) {
    throw Object.assign(new Error('unsupported request command'), {
      name: 'AdapterProtocolError',
      operationId,
    });
  }

  requireJsonValue(parsed.payload, '$.payload');

  return {
    protocolVersion,
    operationId,
    command,
    payload: parsed.payload,
  };
};

const ensureInitialized = () => {
  if (!initialized || !mongoose || !User || !primary || !secondary || !jwt) {
    const error = new Error('adapter runtime is not initialized');
    error.name = 'AdapterRuntimeError';
    throw error;
  }
};

const initializeRuntime = async () => {
  if (!initialized) {
    const mongooseModule = await import('../../../../server/node_modules/mongoose/index.js');
    const jwtModule = await import('../../../../server/node_modules/jsonwebtoken/index.js');

    mongoose = mongooseModule.default;
    jwt = jwtModule.default;

    process.env.MONGODB_URI = mongoUri();
    process.env.MONGO_URI = mongoUri();

    User = (await import('../../../../server/models/userModel.js')).default;
    primary = await import('../../../../server/middleware/authMiddleware.js');
    secondary = await import('../../../../server/middleware/auth.middleware.js');

    await mongoose.connect(mongoUri(), {
      serverSelectionTimeoutMS: SELECTION_TIMEOUT_MS,
      heartbeatFrequencyMS: HEARTBEAT_FREQUENCY_MS,
    });

    initialized = true;
  }

  return {
    node_version: process.version,
    server_mongoose_ready_state: mongoose.connection.readyState,
    user_db_ready_state: User.db.readyState,
    same_mongoose_base: User.db.base === mongoose,
    database_name: User.db.name,
  };
};

const buildSyntheticPasswordHash = (email, tenantId) =>
  crypto
    .createHash('sha3-512')
    .update(`wilsy-auth-cert-fixture|${email}|${tenantId}`)
    .digest('hex');

const buildSyntheticUsername = (email, tenantId) =>
  `wilsy_auth_cert_${crypto
    .createHash('sha3-256')
    .update(`${email}|${tenantId}`)
    .digest('hex')
    .slice(0, 24)}`;

const provisionFixture = async (payload) => {
  ensureInitialized();
  requireExactKeys(
    payload,
    ['synthetic_email', 'synthetic_tenant_value'],
    'PROVISION_FIXTURE payload'
  );

  const email = requireTrimmedString(payload.synthetic_email, 'synthetic_email').toLowerCase();
  const tenantId = requireNullableTrimmedString(
    payload.synthetic_tenant_value,
    'synthetic_tenant_value'
  );

  if (tenantId === null) {
    const error = new Error('synthetic tenant-shaped value is required by the real User model');
    error.name = 'FixtureProvisionError';
    throw error;
  }

  const user = new User({
    username: buildSyntheticUsername(email, tenantId),
    email,
    tenantId,
    passwordHash: buildSyntheticPasswordHash(email, tenantId),
    metadata: {
      wilsyAuthOutageCertificationFixture: true,
    },
  });

  await user.save();

  const durableUserId = String(user._id);
  fixtureRegistry.set(durableUserId, {
    tenantId,
  });

  return {
    operation_succeeded: true,
    durable_user_id: durableUserId,
    database_name: User.db.name,
  };
};

const lookupFixture = async (payload) => {
  ensureInitialized();
  requireExactKeys(payload, ['durable_user_id'], 'LOOKUP_FIXTURE payload');

  const durableUserId = requireTrimmedString(payload.durable_user_id, 'durable_user_id');

  const foundUser = await User.findById(durableUserId).select('_id tenantId').lean();
  const found = foundUser !== null;

  if (found && !fixtureRegistry.has(durableUserId)) {
    fixtureRegistry.set(durableUserId, {
      tenantId: String(foundUser.tenantId || ''),
    });
  }

  return {
    lookup_succeeded: true,
    found,
    durable_user_id: found ? String(foundUser._id) : null,
    database_name: User.db.name,
  };
};

const deleteFixture = async (payload) => {
  ensureInitialized();
  requireExactKeys(payload, ['durable_user_id'], 'DELETE_FIXTURE payload');

  const durableUserId = requireTrimmedString(payload.durable_user_id, 'durable_user_id');

  const result = await User.deleteOne({ _id: durableUserId });
  fixtureRegistry.delete(durableUserId);

  return {
    delete_succeeded: true,
    deleted: result.deletedCount === 1,
    durable_user_id: durableUserId,
    database_name: User.db.name,
  };
};

const scenarioDefinition = (scenarioId, durableUserId) => {
  const fixture = fixtureRegistry.get(durableUserId);

  switch (scenarioId) {
    case 'PRIMARY_USER_FOUND':
      return { middleware: primary.protect, claims: {} };
    case 'PRIMARY_SOVEREIGN_USER_FOUND':
      return { middleware: primary.sovereignAuthenticate, claims: {} };
    case 'SECONDARY_USER_FOUND':
      return { middleware: secondary.protect, claims: {} };
    case 'PRIMARY_DB_FAILURE':
      return { middleware: primary.protect, claims: {} };
    case 'PRIMARY_PRIVILEGED_ROLE_DB_FAILURE':
      return { middleware: primary.protect, claims: { role: 'SUPER_ADMIN' } };
    case 'PRIMARY_SECURITY_CLEARANCE_DB_FAILURE':
      return {
        middleware: primary.protect,
        claims: { securityClearance: 'TOP_SECRET' },
      };
    case 'PRIMARY_TENANT_DB_FAILURE':
      return {
        middleware: primary.protect,
        claims: { tenantId: fixture.tenantId },
      };
    case 'PRIMARY_SOVEREIGN_DB_FAILURE':
      return { middleware: primary.sovereignAuthenticate, claims: {} };
    case 'SECONDARY_DB_FAILURE':
      return { middleware: secondary.protect, claims: {} };
    case 'SECONDARY_PRIVILEGED_ROLE_DB_FAILURE':
      return {
        middleware: secondary.protect,
        claims: { role: 'SUPER_ADMIN' },
      };
    case 'DESIGNATED_EMAIL_DB_FAILURE':
      return {
        middleware: secondary.protect,
        claims: { email: 'synthetic-designated@example.invalid' },
      };
    case 'SECONDARY_SECURITY_CLEARANCE_DB_FAILURE':
      return {
        middleware: secondary.protect,
        claims: { securityClearance: 'TOP_SECRET' },
      };
    case 'SECONDARY_TENANT_DB_FAILURE':
      return {
        middleware: secondary.protect,
        claims: { tenantId: fixture.tenantId },
      };
    default: {
      const error = new Error('scenario is outside the closed registry');
      error.name = 'AdapterProtocolError';
      throw error;
    }
  }
};

const mintSyntheticToken = (durableUserId, claims) =>
  jwt.sign(
    {
      id: durableUserId,
      ...claims,
    },
    EPHEMERAL_JWT_SECRET,
    {
      algorithm: 'HS512',
      expiresIn: '5m',
    }
  );

const invokeMiddleware = async (middleware, durableUserId, claims) => {
  const token = mintSyntheticToken(durableUserId, claims);
  const req = {
    headers: {
      authorization: `Bearer ${token}`,
    },
    cookies: {},
    originalUrl: '/__wilsy_auth_outage_cert__/protected',
    url: '/__wilsy_auth_outage_cert__/protected',
    path: '/__wilsy_auth_outage_cert__/protected',
    method: 'GET',
    get(name) {
      const key = String(name || '').toLowerCase();
      return this.headers[key];
    },
  };

  const observation = {
    statusCode: null,
    body: null,
    nextCount: 0,
  };

  const res = {
    status(code) {
      observation.statusCode = code;
      return res;
    },
    json(body) {
      observation.body = body;
      return res;
    },
  };

  await middleware(req, res, () => {
    observation.nextCount += 1;
  });

  return {
    middlewareCompleted: true,
    nextCount: observation.nextCount,
    hasAuthenticatedUser: Boolean(req.user),
    httpStatus: observation.statusCode,
    responseCode: boundedStringOrNull(observation.body?.error, MAX_RESPONSE_CODE_LENGTH),
  };
};

const observePersistenceFailure = async (durableUserId) => {
  try {
    await User.findById(durableUserId).select('_id').lean();
    return {
      persistence_error_name: null,
      persistence_error_category: null,
      persistence_error_message_sanitized: null,
    };
  } catch (error) {
    return {
      persistence_error_name: boundedStringOrNull(error?.name, 120),
      persistence_error_category: boundedStringOrNull(
        typeof error?.code === 'string' || typeof error?.code === 'number'
          ? String(error.code)
          : null,
        120
      ),
      persistence_error_message_sanitized: sanitizeDiagnostic(error?.message),
    };
  }
};

const runScenario = async (payload) => {
  ensureInitialized();
  requireExactKeys(payload, ['scenario_id', 'parameters'], 'RUN_SCENARIO payload');

  const scenarioId = requireTrimmedString(payload.scenario_id, 'scenario_id');
  if (!SCENARIOS.includes(scenarioId)) {
    const error = new Error('scenario is outside the closed registry');
    error.name = 'AdapterProtocolError';
    throw error;
  }

  requireExactKeys(payload.parameters, ['durable_user_id'], 'RUN_SCENARIO parameters');
  const durableUserId = requireTrimmedString(payload.parameters.durable_user_id, 'durable_user_id');

  if (!fixtureRegistry.has(durableUserId)) {
    const error = new Error('scenario durable identity is not owned by this adapter runtime');
    error.name = 'AdapterRuntimeError';
    throw error;
  }

  const definition = scenarioDefinition(scenarioId, durableUserId);
  const started = process.hrtime.bigint();

  const persistence = OUTAGE_SCENARIOS.has(scenarioId)
    ? await observePersistenceFailure(durableUserId)
    : {
        persistence_error_name: null,
        persistence_error_category: null,
        persistence_error_message_sanitized: null,
      };

  const middlewareObservation = await invokeMiddleware(
    definition.middleware,
    durableUserId,
    definition.claims
  );

  const elapsedMs = Math.max(0, Math.floor(Number(process.hrtime.bigint() - started) / 1e6));

  return {
    protocol_version: PROTOCOL_VERSION,
    scenario_id: scenarioId,
    middleware_completed: requireBoolean(
      middlewareObservation.middlewareCompleted,
      'middleware_completed'
    ),
    next_count: middlewareObservation.nextCount,
    has_authenticated_user: middlewareObservation.hasAuthenticatedUser,
    http_status: middlewareObservation.httpStatus,
    elapsed_ms: elapsedMs,
    response_code: middlewareObservation.responseCode,
    persistence_error_name: persistence.persistence_error_name,
    persistence_error_category: persistence.persistence_error_category,
    persistence_error_message_sanitized: persistence.persistence_error_message_sanitized,
  };
};

const closeRuntime = async () => {
  if (closing) return;
  closing = true;

  if (mongoose && mongoose.connection.readyState !== 0) {
    await mongoose.disconnect();
  }

  initialized = false;
  fixtureRegistry.clear();
};

const dispatch = async ({ command, payload }) => {
  switch (command) {
    case 'INITIALIZE_RUNTIME':
      requireExactKeys(payload, [], 'INITIALIZE_RUNTIME payload');
      return { type: 'READY', payload: await initializeRuntime() };

    case 'PROVISION_FIXTURE':
      return { type: 'RESULT', payload: await provisionFixture(payload) };

    case 'LOOKUP_FIXTURE':
      return { type: 'RESULT', payload: await lookupFixture(payload) };

    case 'DELETE_FIXTURE':
      return { type: 'RESULT', payload: await deleteFixture(payload) };

    case 'RUN_SCENARIO':
      return { type: 'RESULT', payload: await runScenario(payload) };

    case 'CLOSE_RUNTIME':
      requireExactKeys(payload, [], 'CLOSE_RUNTIME payload');
      await closeRuntime();
      return { type: 'SHUTDOWN_COMPLETE', payload: {} };

    default: {
      const error = new Error('unsupported request command');
      error.name = 'AdapterProtocolError';
      throw error;
    }
  }
};

const rl = readline.createInterface({
  input: process.stdin,
  crlfDelay: Infinity,
  terminal: false,
});

try {
  for await (const rawLine of rl) {
    if (closing) break;

    const line = String(rawLine);
    if (!line.trim()) {
      writeDiagnostic('[AUTH_OUTAGE_ADAPTER] Ignored empty stdin line');
      continue;
    }

    let operationId = 'UNAVAILABLE';

    try {
      const request = parseRequestLine(line);
      operationId = request.operationId;

      const response = await dispatch(request);
      await writeEnvelope(operationId, response.type, response.payload);

      if (request.command === 'CLOSE_RUNTIME') {
        rl.close();
        process.stdin.pause();
        break;
      }
    } catch (error) {
      if (error && typeof error.operationId === 'string' && error.operationId.trim()) {
        operationId = error.operationId.trim();
      }

      await writeError(operationId, error);
    }
  }
} catch (error) {
  writeDiagnostic(
    '[AUTH_OUTAGE_ADAPTER] transport loop failed:',
    sanitizeDiagnostic(error?.message) || error?.name || 'unknown failure'
  );
  process.exitCode = 1;
} finally {
  if (!closing && mongoose && mongoose.connection.readyState !== 0) {
    try {
      await mongoose.disconnect();
    } catch (error) {
      writeDiagnostic(
        '[AUTH_OUTAGE_ADAPTER] final disconnect failed:',
        sanitizeDiagnostic(error?.message) || error?.name || 'unknown failure'
      );
      process.exitCode = 1;
    }
  }
}

/**
 * =============================================================================
 * WILSY OS SOVEREIGN FOREIGN-RUNTIME ADAPTER SEAL
 * =============================================================================
 *
 * ARTIFACT:
 *   WILSY OS Authentication Outage Node Observation Adapter
 *
 * VERSION:
 *   v1.0.0-PYTHON-CROSS-CERT-ADAPTER
 *
 * AUTHORITY BOUNDARY:
 *   Foreign-runtime observation only. Python owns certification orchestration,
 *   verdict derivation, canonical evidence, hashing, status, and restoration.
 *
 * TENANT POSTURE:
 *   Synthetic fixture data only; no tenant-membership or authorization authority.
 *
 * FAIL-CLOSED POSTURE:
 *   Malformed transport, invalid command/payload, runtime failure, persistence
 *   ambiguity, or shutdown failure cannot be converted into a successful fact.
 *
 * FINANCIAL EXECUTION AUTHORITY:
 *   None. Kennel EOS remains the exclusive financial execution authority.
 *
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * =============================================================================
 */
