/**
 * WILSY OS — C1C/C1E CLIENT TRANSPORT ADAPTER
 *
 * TITLE: Dedicated legal-services and next-actions browser transport
 * VERSION: v1.0.0-C1E-R1B
 * AUTHORITY: Wilsy OS Core Governance; transport contract only
 * EPITOME: Provides three explicit browser operations over the certified R1A
 *          BFF without creating legal, advisory, persistence, or financial truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/wilsyAIAdvisoryApi.js
 * COLLABORATION / OWNERSHIP: Existing sovereign api.js client; Python EOS C1C/C1E routes.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.0-C1E-R1B — Added bounded C1C/C1E transport primitives.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Authentication and tenant headers remain owned by api.js.
 * TENANT BOUNDARY: No tenant is accepted in payloads or derived in this adapter.
 * AUTHORITY BOUNDARY: Python EOS remains authoritative for authorization and advisory truth.
 * FINANCIAL AUTHORITY BOUNDARY: No quotation, invoice, payment, settlement, or execution authority.
 */

import api from './api.js';

const C1C_LEGAL_SERVICES_PATH = '/wilsy-ai/legal-services';
const C1E_LEGAL_NEXT_ACTIONS_PATH = '/wilsy-ai/legal-next-actions';

/**
 * Validate a required transport identifier without rewriting caller content.
 *
 * @param {unknown} value - Caller-supplied value.
 * @param {string} name - Public input name used in the deterministic error.
 * @returns {string} The exact caller-supplied string.
 * @throws {TypeError} When the input is absent or not a non-empty string.
 */
const requireTransportString = (value, name) => {
  if (typeof value !== 'string' || value.length === 0) {
    throw new TypeError(`${name} must be a non-empty string`);
  }
  return value;
};

/**
 * Preserve only the adapter's documented transport envelope.
 *
 * @param {{status: number, data: unknown}} response - Axios response from the sovereign client.
 * @returns {{status: number, data: unknown}} Exact HTTP status and response payload.
 * @collaboration Python EOS supplies status and domain payload; callers decide presentation.
 * @institutional Prevents client-side reinterpretation of legal advisory truth.
 */
const toTransportEnvelope = (response) => ({
  status: response.status,
  data: response.data,
});

/**
 * Execute the bounded C1C legal-services orchestration transport.
 *
 * @param {string} prompt - Exact caller prompt sent to Python EOS.
 * @param {string} idempotencyKey - Caller-owned replay key; never generated here.
 * @returns {Promise<{status: number, data: unknown}>} Preserved server response envelope.
 * @throws {TypeError} For structurally absent inputs.
 * @throws {unknown} The original Axios rejection for server or transport failures.
 * @institutional C1C remains the sole orchestration authority; this function performs no chaining.
 */
export const executeWilsyAILegalServices = async (prompt, idempotencyKey) => {
  const exactPrompt = requireTransportString(prompt, 'prompt');
  const exactIdempotencyKey = requireTransportString(idempotencyKey, 'idempotencyKey');
  const response = await api.post(
    C1C_LEGAL_SERVICES_PATH,
    { prompt: exactPrompt },
    { headers: { 'Idempotency-Key': exactIdempotencyKey } },
  );
  return toTransportEnvelope(response);
};

/**
 * Request a C1E next-actions advisory for an existing orchestration.
 *
 * @param {string} orchestrationId - Exact C1C orchestration identifier.
 * @returns {Promise<{status: number, data: unknown}>} Preserved server response envelope.
 * @throws {TypeError} For a structurally absent orchestration identifier.
 * @throws {unknown} The original Axios rejection for server or transport failures.
 * @institutional C1E generation remains an explicit caller action; no C1C or GET chaining occurs.
 */
export const generateWilsyAILegalNextActions = async (orchestrationId) => {
  const exactOrchestrationId = requireTransportString(orchestrationId, 'orchestrationId');
  const response = await api.post(C1E_LEGAL_NEXT_ACTIONS_PATH, {
    orchestration_id: exactOrchestrationId,
  });
  return toTransportEnvelope(response);
};

/**
 * Read one persisted C1E advisory by its encoded identity.
 *
 * @param {string} advisoryId - Exact advisory identifier supplied by the caller.
 * @returns {Promise<{status: number, data: unknown}>} Preserved server response envelope.
 * @throws {TypeError} For a structurally absent advisory identifier.
 * @throws {unknown} The original Axios rejection for server or transport failures.
 * @institutional Python EOS owns tenant scope, CURRENT/STALE derivation, and replay semantics.
 */
export const readWilsyAILegalNextAction = async (advisoryId) => {
  const exactAdvisoryId = requireTransportString(advisoryId, 'advisoryId');
  const response = await api.get(
    `${C1E_LEGAL_NEXT_ACTIONS_PATH}/${encodeURIComponent(exactAdvisoryId)}`,
  );
  return toTransportEnvelope(response);
};

// ARTIFACT: wilsyAIAdvisoryApi.js
// VERSION: v1.0.0-C1E-R1B
// AUTHORITY BOUNDARY: transport primitives only; Python EOS is sovereign
// TENANT POSTURE: api.js owns authenticated tenant context; no local derivation
// FAIL-CLOSED POSTURE: Axios failures reject unchanged; no fallback advisory is created
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
