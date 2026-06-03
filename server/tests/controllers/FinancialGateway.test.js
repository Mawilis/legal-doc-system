/* eslint-disable */
/**
 * 🧪 FinancialGateway Forensic Audit
 * @description Verifying the unification of Billing and Tax logic.
 */
import { expect } from 'chai';
import { generateFinalSovereignInvoice } from '../../controllers/finance/FinancialGateway.controller.js';

describe('🏛️ FinancialGateway Forensic Audit', () => {
  let mockReq;
  let mockRes;

  beforeEach(() => {
    mockReq = {
      body: {
        tenantId: 'TENANT-ZA-CENTRAL',
        tenantData: { jurisdiction: 'ZA', documentCount: 0 }
      }
    };
    mockRes = {
      status: function(code) { this.statusCode = code; return this; },
      json: function(data) { this.body = data; return this; },
      statusCode: null,
      body: null
    };
  });

  it('generates a final sealed invoice with both platform fees and jurisdictional VAT', async () => {
    await generateFinalSovereignInvoice(mockReq, mockRes);

    // Base: R45.7M | 10% Fee = R4.57M | 15% VAT = R685.5K | Total = R5,255,500
    expect(mockRes.statusCode).to.equal(200);
    expect(mockRes.body.subtotal).to.equal(4570000);
    expect(mockRes.body.taxAmount).to.equal(685500);
    expect(mockRes.body.totalDue).to.equal(5255500);
    expect(mockRes.body.masterSignature).to.have.lengthOf(128);
    expect(mockRes.body.status).to.equal('SEALED');
  });
});
