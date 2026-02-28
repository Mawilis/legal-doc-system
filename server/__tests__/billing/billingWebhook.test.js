/* eslint-env mocha */
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ BILLING WEBHOOK TESTS - REAL-TIME REVENUE INTEGRATION                     ║
  ║ Tests Paystack/Stripe webhooks | Dividend triggers | Forensic audit       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { expect } from 'chai';
import sinon from 'sinon';
import request from 'supertest';
import express from 'express';
import crypto from 'crypto';

import { handleWebhook } from '../../controllers/billing/billingWebhookController.js';
import * as payoutService from '../../services/finance/payoutService.js';
import ValidationAudit from '../../models/ValidationAudit.js';
import { ApiKey } from '../../models/api/ApiKey.js';

describe('💳 BILLING WEBHOOK - LIVE REVENUE INTEGRATION', () => {
  let app;
  let sandbox;

  beforeEach(() => {
    sandbox = sinon.createSandbox();
    
    // Mock payout service
    sandbox.stub(payoutService, 'calculateInvestorDividends').returns({
      success: true,
      forensicId: 'PAY-123456789-ABCD',
      summary: {
        investorPayout: 1000000,
        founderPayout: 1200000,
        totalPayout: 2200000
      },
      dividends: {
        investors: [{ name: 'Test Investor', dividend: 1000000 }],
        founder: { dividend: 1200000 }
      }
    });

    // Mock ValidationAudit
    sandbox.stub(ValidationAudit, 'create').resolves({});
    
    // Mock ApiKey
    sandbox.stub(ApiKey, 'findOneAndUpdate').resolves({});

    // Create test app
    app = express();
    app.use(express.json());
    app.post('/webhook', handleWebhook);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('Paystack Webhook', () => {
    
    it('should process successful payment and trigger dividends', async () => {
      const payload = {
        event: 'charge.success',
        data: {
          amount: 325000000, // R3.25M in cents
          reference: 'test-ref-123',
          metadata: {
            tenantId: 'test-tenant-123',
            subscriptionId: 'sub-456'
          },
          customer: {
            email: 'firm@example.com'
          }
        }
      };

      const response = await request(app)
        .post('/webhook')
        .set('x-paystack-signature', 'test-signature')
        .set('x-correlation-id', 'test-corr-001')
        .send(payload);

      expect(response.status).to.equal(200);
      expect(response.body.success).to.be.true;
      expect(payoutService.calculateInvestorDividends.called).to.be.true;
      expect(ValidationAudit.create.called).to.be.true;
    });

    it('should reject invalid signature', async () => {
      const payload = { event: 'charge.success', data: {} };

      const response = await request(app)
        .post('/webhook')
        .set('x-paystack-signature', 'invalid')
        .send(payload);

      expect(response.status).to.equal(401);
      expect(payoutService.calculateInvestorDividends.called).to.be.false;
    });
  });

  describe('Stripe Webhook', () => {
    
    it('should process successful invoice payment', async () => {
      const payload = {
        type: 'invoice.payment_succeeded',
        data: {
          object: {
            id: 'inv-123',
            amount_paid: 32500000, // R325,000 in cents
            subscription: 'sub-456',
            metadata: {
              tenantId: 'test-tenant-123'
            },
            next_payment_attempt: Date.now() + 30 * 24 * 60 * 60 * 1000
          }
        }
      };

      const response = await request(app)
        .post('/webhook')
        .set('stripe-signature', 'test-signature')
        .set('x-correlation-id', 'test-corr-001')
        .send(payload);

      expect(response.status).to.equal(200);
      expect(payoutService.calculateInvestorDividends.called).to.be.true;
      expect(ValidationAudit.create.called).to.be.true;
    });
  });
});
