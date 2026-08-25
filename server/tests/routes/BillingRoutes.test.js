/* eslint-disable */
/*
 * WILSY OS - BILLING CONTRACT ROUTE VALIDATION SUITE
 * [COMMAND CONTRACTS | PROOF HASHING | REQUEST SCHEMA | FORENSIC VALIDATION]
 * ---------------------------------------------------------------------------
 * Architect: Wilson Khanyezi
 * Purpose: Verify new BillingHUD contract endpoints for legal, tax, dunning,
 *          telemetry, and treasury command surfaces.
 */

import { expect } from 'chai';
import request from 'supertest';
import express from 'express';
import billingRoutes from '../../routes/billingRoutes.js';
import { hashData } from '../../utils/cryptoCore.js';

const app = express();
app.use(express.json());
app.use('/api/billing', billingRoutes);

describe('Billing Routes - Command Contract API', function () {
    it('POST /api/billing/legal should accept a valid legal command envelope', async function () {
        const payload = {
            commandType: 'LEGAL_ROUTE',
            commandVersion: 'V2.0.0-LIVE-DB',
            tenantId: 'tenant-a',
            generatedAt: new Date().toISOString()
        };
        const proofHash = hashData(payload).toUpperCase();

        const res = await request(app)
            .post('/api/billing/legal')
            .send({ ...payload, proofHash })
            .expect(200);

        expect(res.body.success).to.be.true;
        expect(res.body.commandType).to.equal('LEGAL_ROUTE');
        expect(res.body.surface).to.equal('BILLING_LEGAL_ROUTE');
        expect(res.body.proofHash).to.equal(proofHash);
    });

    it('POST /api/billing/tax should enforce taxProfile schema and proof validation', async function () {
        const payload = {
            commandType: 'SEAL_TAX_POSTURE',
            commandVersion: 'V2.0.0-LIVE-DB',
            tenantId: 'tenant-b',
            generatedAt: new Date().toISOString(),
            taxProfile: {
                jurisdiction: 'ZA',
                effectiveDate: new Date().toISOString(),
                taxStatus: 'COMPLIANT'
            }
        };
        const proofHash = hashData(payload).toUpperCase();

        const res = await request(app)
            .post('/api/billing/tax')
            .send({ ...payload, proofHash })
            .expect(200);

        expect(res.body.success).to.be.true;
        expect(res.body.surface).to.equal('BILLING_SEAL_TAX_POSTURE');
        expect(res.body.data.payload.taxProfile).to.deep.equal(payload.taxProfile);
    });

    it('POST /api/billing/dunning should reject invalid proof hash', async function () {
        const payload = {
            commandType: 'RUN_DUNNING',
            commandVersion: 'V2.0.0-LIVE-DB',
            tenantId: 'tenant-c',
            generatedAt: new Date().toISOString(),
            overdueCount: 3
        };

        const res = await request(app)
            .post('/api/billing/dunning')
            .send({ ...payload, proofHash: 'INVALIDPROOFHASH' })
            .expect(400);

        expect(res.body.success).to.be.false;
        expect(res.body.status).to.equal('PROOF_VALIDATION_FAILED');
        expect(res.body.error).to.equal('PROOF_HASH_INVALID');
    });

    it('POST /api/billing/telemetry should validate required telemetry fields', async function () {
        const payload = {
            commandType: 'BROADCAST_TELEMETRY',
            commandVersion: 'V2.0.0-LIVE-DB',
            tenantId: 'tenant-d',
            generatedAt: new Date().toISOString(),
            circuitBreaker: 'CLOSED',
            avgLatencyMs: 12,
            forensicSeal: 'FOR-TELEMETRY-001'
        };
        const proofHash = hashData(payload).toUpperCase();

        const res = await request(app)
            .post('/api/billing/telemetry')
            .send({ ...payload, proofHash })
            .expect(200);

        expect(res.body.success).to.be.true;
        expect(res.body.surface).to.equal('BILLING_BROADCAST_TELEMETRY');
        expect(res.body.data.payload.avgLatencyMs).to.equal(12);
    });

    it('POST /api/billing/treasury should reject mismatched commandType route', async function () {
        const payload = {
            commandType: 'LEGAL_ROUTE',
            commandVersion: 'V2.0.0-LIVE-DB',
            tenantId: 'tenant-e',
            generatedAt: new Date().toISOString(),
            currency: 'ZAR',
            currentBalance: 100000
        };
        const proofHash = hashData(payload).toUpperCase();

        const res = await request(app)
            .post('/api/billing/treasury')
            .send({ ...payload, proofHash })
            .expect(400);

        expect(res.body.success).to.be.false;
        expect(res.body.error).to.equal('COMMAND_TYPE_MISMATCH');
    });
});
