/* eslint-disable */
/**
 * WILSY OS — Legacy Signature Service Compatibility Boundary
 *
 * VERSION: v2.0.0-P0-C4C-R5-RETIRED
 * AUTHORITY: Wilsy OS server compatibility boundary
 *
 * PURPOSE:
 *   Preserve the historical module path and export names while retiring the
 *   unused legacy provider / pseudo-certificate-authority implementation.
 *
 * SECURITY BOUNDARIES:
 *   - This module does not issue certificates.
 *   - This module does not operate a certificate authority.
 *   - This module does not assert statutory compliance, legal validity,
 *     evidential weight, accreditation, non-repudiation, or court admissibility.
 *   - This module does not call DocuSign, SignRequest, or any other provider.
 *   - All legacy operational entry points fail closed.
 *
 * MIGRATION:
 *   Active cryptographic document-signing capability is provided separately by
 *   server/services/digitalSignatureService.js.
 *
 * CHANGELOG:
 *   - Retired the unreachable legacy node-forge certificate implementation.
 *   - Removed broken imports and import-time environment validation.
 *   - Removed fabricated compliance/provider authority claims.
 *   - Preserved historical export names as fail-closed compatibility shims.
 */

const RETIRED_SIGNATURE_SERVICE_CODE = 'LEGACY_SIGNATURE_SERVICE_RETIRED';

const RETIRED_SIGNATURE_SERVICE_MESSAGE =
  'Legacy signatureService is retired; use digitalSignatureService for certified cryptographic signing capability.';

const retiredSignatureServiceError = () => {
  const error = new Error(RETIRED_SIGNATURE_SERVICE_MESSAGE);
  error.code = RETIRED_SIGNATURE_SERVICE_CODE;
  return error;
};

const QUANTUM_CONSTANTS = Object.freeze({
  STATUS: 'RETIRED',
  MIGRATION_TARGET: 'server/services/digitalSignatureService.js',
});

class QuantumCertificateAuthority {
  constructor() {
    this.initialized = false;
  }

  async initialize() {
    throw retiredSignatureServiceError();
  }

  async generateCACertificate() {
    throw retiredSignatureServiceError();
  }

  async issueCertificate() {
    throw retiredSignatureServiceError();
  }

  async validateCertificate() {
    throw retiredSignatureServiceError();
  }

  async revokeCertificate() {
    throw retiredSignatureServiceError();
  }
}

class SignatureProvider {
  constructor(providerType) {
    this.providerType = providerType;
    this.initialized = false;
  }

  loadProviderConfig() {
    throw retiredSignatureServiceError();
  }

  async initialize() {
    throw retiredSignatureServiceError();
  }

  async initializeDocuSign() {
    throw retiredSignatureServiceError();
  }

  async initializeSignRequest() {
    throw retiredSignatureServiceError();
  }

  async createSignatureRequest() {
    throw retiredSignatureServiceError();
  }

  async createDocuSignEnvelope() {
    throw retiredSignatureServiceError();
  }

  async createSignRequest() {
    throw retiredSignatureServiceError();
  }

  async createInternalSignature() {
    throw retiredSignatureServiceError();
  }
}

export {
  SignatureProvider,
  QuantumCertificateAuthority,
  QUANTUM_CONSTANTS,
  RETIRED_SIGNATURE_SERVICE_CODE,
};

export default {
  SignatureProvider,
  QuantumCertificateAuthority,
  QUANTUM_CONSTANTS,
  RETIRED_SIGNATURE_SERVICE_CODE,
};

// ============================================================================
// END SEAL — WILSY OS LEGACY SIGNATURE SERVICE v2.0.0-P0-C4C-R5-RETIRED
// Historical compatibility path only; no operational signing authority.
// ============================================================================
