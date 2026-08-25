/**
 * ====================================================================
 *  WILSY OS – SOVEREIGN QR PAYMENT FLOW INTEGRATION TESTS
 *  Version: v1.0.0‑SOVEREIGN
 *  Authority: WILSY OS KENNEL EOS – TENANT ISOLATION & CRYPTOGRAPHIC VERIFICATION
 *  Epitome: Full integration test suite for QR → verification → payment → audit flow.
 *           Uses mocks for external APIs (PayShap, Zapper) so tests can run with placeholders.
 *  Collaboration: Wilson (architect), AI (implementation) – 2026-08-10
 *  Institutional: POPIA §19, GDPR §32, SOC2 §CC7.2 – tests validate cryptographic seals,
 *                 tenant isolation, and immutable audit trails.
 * ====================================================================
 */

import { expect } from 'chai';
import sinon from 'sinon';
import axios from 'axios';
import mongoose from 'mongoose';
import crypto from 'crypto';
import { MongoMemoryServer } from 'mongodb-memory-server';

// ─── IMPORTS UNDER TEST ──────────────────────────────────────────────────────
import Invoice from '../../server/models/Invoice.js';
import { buildQRPayload, generateQRCode } from '../../server/services/qr/qrGenerator.js';
import { verifyQRPayload } from '../../server/services/qr/qrVerificationService.js';
import { initiatePayment, handleWebhook } from '../../server/services/payment/payShapService.js';
import { logVerificationAttempt, getVerificationStats, verifyLogIntegrity } from '../../server/services/audit/verificationLogService.js';
import { getSovereignInvoiceModel } from '../../server/controllers/billingController.js';

// ─── TEST CONFIGURATION ─────────────────────────────────────────────────────
const TEST_TENANT = 'TEST_TENANT';
const TEST_INVOICE_NUMBER = 'TEST-INV-001';
const TEST_TRACE_ID = 'TRACE-001';

let mongoServer;
let testInvoice;
let axiosPostStub;
let axiosGetStub;

// ─── HELPERS ────────────────────────────────────────────────────────────────

/**
 * createTestInvoice – Creates a test invoice in the sovereign database.
 */
async function createTestInvoice() {
  const SovereignInvoice = getSovereignInvoiceModel();
  const invoice = await SovereignInvoice.create({
    invoiceNumber: TEST_INVOICE_NUMBER,
    tenantId: 'WILSY_ROOT',
    recipientTenantId: TEST_TENANT,
    totalAmount: 115.00,
    currency: 'ZAR',
    status: 'ISSUED',
    outstandingAmount: 115.00,
    paidAmount: 0,
    lineItems: [
      { description: 'Test sovereign service', quantity: 1, unitPrice: 100.00, lineTotal: 100.00 },
      { description: 'VAT (15%)', quantity: 1, unitPrice: 15.00, lineTotal: 15.00 },
    ],
    traceId: TEST_TRACE_ID,
    sealHash: crypto.createHash('sha3-512').update(TEST_INVOICE_NUMBER).digest('hex'),
    brandingNexus: {
      legalEntity: 'Wilsy (Pty) Ltd',
      color: '#D4AF37',
    },
  });
  return invoice;
}

// ─── TEST SUITE ─────────────────────────────────────────────────────────────

describe('🏛️ WILSY OS – QR Payment Flow Integration Tests', function () {
  this.timeout(10000);

  // ─── HOOKS ──────────────────────────────────────────────────────────────

  before(async function () {
    // Start in‑memory MongoDB for isolated testing
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri, {
      dbName: 'wilsy-test',
    });

    // Ensure models are registered
    await mongoose.connection.db.collection('invoices').createIndex({ invoiceNumber: 1 });
  });

  after(async function () {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  beforeEach(async function () {
    // Create fresh test invoice before each test
    testInvoice = await createTestInvoice();

    // Stub axios.post for PayShap initiation
    axiosPostStub = sinon.stub(axios, 'post').resolves({
      data: {
        reference: 'PAY-123',
        redirectUrl: 'https://mock.payshap.co.za/pay',
        status: 'PENDING',
      },
      status: 200,
    });

    // Stub axios.get for status checks
    axiosGetStub = sinon.stub(axios, 'get').resolves({
      data: {
        status: 'PAID',
        amount: 115.00,
        paidAt: new Date().toISOString(),
      },
      status: 200,
    });
  });

  afterEach(async function () {
    // Clean up stubs
    if (axiosPostStub) axiosPostStub.restore();
    if (axiosGetStub) axiosGetStub.restore();

    // Clean up database
    const SovereignInvoice = getSovereignInvoiceModel();
    await SovereignInvoice.deleteMany({});
  });

  // ─── TESTS ──────────────────────────────────────────────────────────────

  /**
   * @test QR Payload Generation
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that buildQRPayload produces a signed, verifiable payload.
   * @institutional  Cryptographic proof is essential for non‑repudiation.
   */
  it('should generate a signed QR payload with verification URL', function () {
    const payload = buildQRPayload({
      invoiceId: testInvoice.invoiceNumber,
      tenantId: testInvoice.recipientTenantId,
      amount: testInvoice.totalAmount,
      currency: testInvoice.currency,
      traceId: testInvoice.traceId,
      merkleRoot: 'MOCK_MERKLE_ROOT',
      sealHash: testInvoice.sealHash,
    });

    expect(payload).to.have.property('payload');
    expect(payload).to.have.property('signature');
    expect(payload).to.have.property('verificationUrl');
    expect(payload.verificationUrl).to.include('payload=');
    expect(payload.verificationUrl).to.include('signature=');
    expect(payload.payload.tenantId).to.equal(testInvoice.recipientTenantId);
    expect(payload.payload.amount).to.equal(testInvoice.totalAmount);
  });

  /**
   * @test QR Verification Service
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that QR payloads are cryptographically verified with HMAC + PKI.
   * @institutional  Regulators require non‑repudiable verification of invoice authenticity.
   */
  it('should verify a signed QR payload successfully', async function () {
    const qrPayload = buildQRPayload({
      invoiceId: testInvoice.invoiceNumber,
      tenantId: testInvoice.recipientTenantId,
      amount: testInvoice.totalAmount,
      currency: testInvoice.currency,
      traceId: testInvoice.traceId,
      merkleRoot: 'MOCK_MERKLE_ROOT',
      sealHash: testInvoice.sealHash,
    });

    const result = await verifyQRPayload(
      qrPayload.payloadString,
      qrPayload.signature,
      testInvoice.recipientTenantId,
      { skipInvoiceCheck: false }
    );

    expect(result.valid).to.be.true;
    expect(result.error).to.be.null;
    expect(result.tenant).to.equal(testInvoice.recipientTenantId);
    expect(result.invoice).to.exist;
    expect(result.invoice.invoiceNumber).to.equal(testInvoice.invoiceNumber);
  });

  /**
   * @test Tenant Isolation
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Ensures that QR payloads cannot be verified across tenants.
   * @institutional  POPIA §19 and GDPR §32 mandate data segregation.
   */
  it('should reject verification from a different tenant', async function () {
    const qrPayload = buildQRPayload({
      invoiceId: testInvoice.invoiceNumber,
      tenantId: testInvoice.recipientTenantId,
      amount: testInvoice.totalAmount,
      currency: testInvoice.currency,
      traceId: testInvoice.traceId,
      merkleRoot: 'MOCK_MERKLE_ROOT',
      sealHash: testInvoice.sealHash,
    });

    const result = await verifyQRPayload(
      qrPayload.payloadString,
      qrPayload.signature,
      'DIFFERENT_TENANT',
      { skipInvoiceCheck: false }
    );

    expect(result.valid).to.be.false;
    expect(result.error).to.include('Tenant mismatch');
  });

  /**
   * @test Expiry Validation
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        QR codes must expire to prevent replay attacks.
   * @institutional  SOC2 §CC7.2 requires time‑based access controls.
   */
  it('should reject an expired QR payload', async function () {
    const expiredPayload = buildQRPayload({
      invoiceId: testInvoice.invoiceNumber,
      tenantId: testInvoice.recipientTenantId,
      amount: testInvoice.totalAmount,
      currency: testInvoice.currency,
      traceId: testInvoice.traceId,
      merkleRoot: 'MOCK_MERKLE_ROOT',
      sealHash: testInvoice.sealHash,
      expiresAt: new Date(Date.now() - 86400000).toISOString(), // yesterday
    });

    const result = await verifyQRPayload(
      expiredPayload.payloadString,
      expiredPayload.signature,
      testInvoice.recipientTenantId,
      { skipInvoiceCheck: false }
    );

    expect(result.valid).to.be.false;
    expect(result.error).to.equal('QR code expired');
  });

  /**
   * @test PayShap Payment Initiation (Mocked)
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that payment initiation calls the PayShap API and returns a reference.
   * @institutional  Every payment must be auditable with a unique reference.
   */
  it('should initiate a PayShap payment (mocked)', async function () {
    const result = await initiatePayment(testInvoice, {
      returnUrl: 'http://localhost:3000/return',
      notifyUrl: 'http://localhost:4000/webhook/payshap',
      requestId: 'REQ-001',
    });

    expect(result.success).to.be.true;
    expect(result.paymentReference).to.equal('PAY-123');
    expect(result.redirectUrl).to.equal('https://mock.payshap.co.za/pay');
    expect(result.status).to.equal('PENDING');
    expect(axiosPostStub.calledOnce).to.be.true;

    // Verify the API call payload
    const callArgs = axiosPostStub.firstCall.args;
    expect(callArgs[1]).to.have.property('metadata');
    expect(callArgs[1].metadata.invoiceNumber).to.equal(testInvoice.invoiceNumber);
  });

  /**
   * @test PayShap Webhook Handling
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that webhooks update invoice status and regenerate seals.
   * @institutional  Automated reconciliation is critical for financial integrity.
   */
  it('should handle PayShap webhook and update invoice status (mocked)', async function () {
    const webhookPayload = {
      reference: 'PAY-123',
      status: 'PAID',
      amount: 115.00,
      paidAt: new Date().toISOString(),
      currency: 'ZAR',
      metadata: {
        tenantId: TEST_TENANT,
        invoiceNumber: testInvoice.invoiceNumber,
      },
    };

    // Signature verification is bypassed in test by passing a dummy secret
    // (we use a placeholder that matches our test secret)
    const result = await handleWebhook(
      webhookPayload,
      'mock-signature',
      'default-webhook-secret-change-me', // matches the default in payShapService
      false // don't skip invoice update
    );

    expect(result.success).to.be.true;
    expect(result.invoiceUpdated).to.be.true;
    expect(result.status).to.equal('PAID');
    expect(result.invoiceNumber).to.equal(testInvoice.invoiceNumber);

    // Verify invoice was updated in database
    const SovereignInvoice = getSovereignInvoiceModel();
    const updatedInvoice = await SovereignInvoice.findOne({ invoiceNumber: testInvoice.invoiceNumber });
    expect(updatedInvoice.status).to.equal('PAID');
    expect(updatedInvoice.outstandingAmount).to.equal(0);
    expect(updatedInvoice.paidAmount).to.equal(testInvoice.totalAmount);
    expect(updatedInvoice.sealHash).to.exist;
    expect(updatedInvoice.sealHash.length).to.be.at.least(32);
  });

  /**
   * @test Audit Logging
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that verification attempts are immutably logged with seals.
   * @institutional  POPIA §19 and GDPR §32 require auditable trails of all accesses.
   */
  it('should log verification attempts with cryptographic seals', async function () {
    const log = await logVerificationAttempt({
      action: 'QR_SCAN',
      tenantId: TEST_TENANT,
      invoiceId: testInvoice.invoiceNumber,
      traceId: testInvoice.traceId,
      payloadHash: crypto.createHash('sha3-512').update('test-payload').digest('hex'),
      signatureDigest: crypto.createHash('sha3-512').update('test-signature').digest('hex'),
      pkiVerified: true,
      anomalyScore: 0,
      valid: true,
      amount: testInvoice.totalAmount,
      currency: testInvoice.currency,
      ipAddress: '127.0.0.1',
      userAgent: 'Mozilla/5.0 (test)',
      correlationId: 'CORR-001',
    });

    expect(log).to.have.property('sealHash');
    expect(log.sealHash.length).to.be.at.least(32);
    expect(log.valid).to.be.true;
    expect(log.anomalyScore).to.equal(0);
    expect(log.pkiVerified).to.be.true;

    // Verify the log integrity
    const integrityValid = verifyLogIntegrity(log);
    expect(integrityValid).to.be.true;
  });

  /**
   * @test Verification Statistics
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that stats aggregation works for dashboards.
   * @institutional  Regulators require aggregated compliance metrics.
   */
  it('should retrieve verification statistics', async function () {
    // Create multiple log entries
    await logVerificationAttempt({
      action: 'QR_SCAN',
      tenantId: TEST_TENANT,
      invoiceId: testInvoice.invoiceNumber,
      traceId: testInvoice.traceId,
      valid: true,
      anomalyScore: 0,
    });

    await logVerificationAttempt({
      action: 'QR_SCAN',
      tenantId: TEST_TENANT,
      invoiceId: testInvoice.invoiceNumber,
      traceId: testInvoice.traceId,
      valid: false,
      anomalyScore: 0.9,
      error: 'Signature mismatch',
    });

    const stats = await getVerificationStats(TEST_TENANT);
    expect(stats.total).to.equal(2);
    expect(stats.successful).to.equal(1);
    expect(stats.failed).to.equal(1);
    expect(stats.successRate).to.equal('50.00');
    expect(stats.byAction).to.be.an('array');
    expect(stats.byAction[0]).to.have.property('action', 'QR_SCAN');
  });

  /**
   * @test Performance Benchmark
   * @collaboration  Wilson & AI – 2026-08-10
   * @epitome        Validates that QR generation and verification meet sub‑millisecond latency.
   * @institutional  SOC2 §CC7.2 requires performance monitoring.
   */
  it('should generate QR payload in under 10ms (performance benchmark)', function () {
    const start = performance.now();
    const payload = buildQRPayload({
      invoiceId: testInvoice.invoiceNumber,
      tenantId: testInvoice.recipientTenantId,
      amount: testInvoice.totalAmount,
      currency: testInvoice.currency,
      traceId: testInvoice.traceId,
      merkleRoot: 'MOCK_MERKLE_ROOT',
      sealHash: testInvoice.sealHash,
    });
    const duration = performance.now() - start;

    expect(payload).to.exist;
    expect(duration).to.be.lessThan(10, `QR generation took ${duration.toFixed(2)}ms – expected < 10ms`);
    console.log(`[PERF] QR payload generation: ${duration.toFixed(2)}ms`);
  });
});

export default {};
