/**
 * ============================================================================
 * WILSY OS - ENTERPRISE SUBSYSTEM VERIFICATION & SEALING TEST SUITE
 * ============================================================================
 *
 * @file         enterprise.test.cjs
 * @directory    server/src/enterprise/
 * @system       Wilsy OS - Enterprise Business Operating Layer (FG231)
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Comprehensive automated test suite verifying kernel immutability,
 *               POPIA redaction, schema validation, workflow state transitions,
 *               and bi-directional graph path traversal using CommonJS bindings.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Governance Engine: Enterprise Domain Isolation & Schema Compliance
 * - Security Standard: Cryptographic Schema Hashing & POPIA/GDPR Schema Enforcement
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | CommonJS sovereign test suite.
 * ============================================================================
 */

const test = require('node:test');
const assert = require('node:assert');

// Pure CommonJS requires matching your sovereign modules
const { EnterpriseKernel, KernelObject, DataRedactor, SecurityKernel, ContextValidator } = require('./kernel/EnterpriseKernel.js');
const { objectRegistryInstance } = require('./registry/EnterpriseObjectRegistry.js');
const { workflowEngineInstance } = require('./workflow/EnterpriseWorkflowEngine.js');
const { graphEngineInstance } = require('./relationships/EnterpriseGraphEngine.js');

test('1. Enterprise Kernel & POPIA Data Redactor Verification', () => {
  const rawText = 'Client ID is 8001015009088 and email is test@wilsyos.com with phone +27821234567';
  const sanitized = DataRedactor.sanitize(rawText);
  assert.strictEqual(sanitized.includes('[REDACTED_SA_ID]'), true, 'SA ID must be redacted');
  assert.strictEqual(sanitized.includes('[REDACTED_EMAIL]'), true, 'Email must be redacted');
  assert.strictEqual(sanitized.includes('[REDACTED_PHONE]'), true, 'Phone must be redacted');

  const payload = {
    name: 'Wilson Khanyezi',
    password: (process.env.TEST_DB_PASSWORD || "redacted-test-secret"),
    taxId: 'TX998877'
  };
  const scrubbedObject = DataRedactor.sanitize(payload);
  assert.strictEqual(scrubbedObject.password, '[REDACTED_SENSITIVE_KEY]', 'Sensitive keys must be redacted');

  const kernelObj = new KernelObject('OBJ-001', 'TENANT-ALPHA', { title: 'Master Agreement' });
  assert.strictEqual(kernelObj.verifyIntegrity(), true, 'KernelObject hash integrity must verify');
  assert.throws(() => {
    kernelObj.payload.title = 'Tampered Agreement';
  }, /Cannot assign to read only property/, 'KernelObject payload must be frozen');
});

test('2. Security Kernel & Context Validator Verification', () => {
  const hash = SecurityKernel.generateStateHash({ status: 'ACTIVE' });
  assert.strictEqual(typeof hash, 'string');
  assert.strictEqual(hash.length, 64, 'SHA-256 hash must be 64 hex chars');

  const hmac = SecurityKernel.generateHMAC('test-payload', 'sovereign-secret');
  assert.strictEqual(typeof hmac, 'string');

  assert.strictEqual(ContextValidator.isValidTenantId('tenant-alpha-1'), true);
  assert.strictEqual(ContextValidator.isValidTenantId('a'), false, 'Tenant ID too short');
});

test('3. Enterprise Object Registry & Schema Validation', () => {
  const customerSchema = objectRegistryInstance.getSchema('CUSTOMER', '1.0.0');
  assert.strictEqual(customerSchema.domain, 'CUSTOMER');
  assert.strictEqual(customerSchema.version, '1.0.0');

  const validValidation = objectRegistryInstance.validateObjectPayload('CUSTOMER', {
    name: 'Acme Corp',
    status: 'ACTIVE',
    email: 'contact@acme.com'
  });
  assert.strictEqual(validValidation.isValid, true, 'Valid customer payload must pass validation');

  const invalidValidation = objectRegistryInstance.validateObjectPayload('CUSTOMER', {
    email: 'incomplete@acme.com'
  });
  assert.strictEqual(invalidValidation.isValid, false, 'Invalid payload must fail validation');
  assert.strictEqual(invalidValidation.errors.length > 0, true);
});

test('4. Shared Workflow Engine & State Transitions', () => {
  const workflow = workflowEngineInstance.createInstance('CONTRACT_LIFECYCLE', 'CONTRACT-100', 'TENANT-ALPHA');
  assert.strictEqual(workflow.currentState, 'DRAFT');

  const reviewed = workflowEngineInstance.transitionState('CONTRACT-100', 'REVIEW', { updatedBy: 'Wilson' });
  assert.strictEqual(reviewed.currentState, 'REVIEW');
  assert.strictEqual(reviewed.history.length, 2);

  assert.throws(() => {
    workflowEngineInstance.transitionState('CONTRACT-100', 'ACTIVE', {});
  }, /Invalid state transition/, 'Disallowed state transitions must throw an error');
});

test('5. Enterprise Relationships & Graph Engine Traversal', () => {
  graphEngineInstance.addEdge('Customer', 'CUST-001', 'Contract', 'CONT-001', 'HAS_CONTRACT');
  graphEngineInstance.addEdge('Contract', 'CONT-001', 'Project', 'PROJ-001', 'GOVERNS_PROJECT');
  graphEngineInstance.addEdge('Project', 'PROJ-001', 'Invoice', 'INV-001', 'PRODUCES_INVOICE');

  const neighborhood = graphEngineInstance.getNeighborhood('Customer', 'CUST-001', 2);
  assert.strictEqual(neighborhood.nodes.length >= 3, true, 'Neighborhood must include connected nodes');

  const path = graphEngineInstance.findPath('Customer', 'CUST-001', 'Invoice', 'INV-001');
  assert.strictEqual(path.length, 4, 'Path from Customer to Invoice must traverse through Contract and Project');

  const diagnostics = graphEngineInstance.runDiagnostics();
  assert.strictEqual(diagnostics.status, 'OPERATIONAL');
  assert.strictEqual(typeof diagnostics.graphSeal, 'string');
});
